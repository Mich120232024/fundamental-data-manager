#!/usr/bin/env python3
"""
FRED Complete Category Hierarchy Collection - Adaptive Rate Version
Dynamically adjusts rate based on rate limit responses
"""

import json
import requests
import time
import os
from datetime import datetime
from collections import deque
import logging
import signal
import sys

# Configuration
API_KEY = "21acd97c4988e53af02e98587d5424d0"
BASE_URL = "https://api.stlouisfed.org/fred"
OUTPUT_DIR = "fred_complete_data"
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "category_collection_checkpoint.json")

# Adaptive rate limiting
MIN_SLEEP_TIME = 0.5  # 120 calls/minute max
MAX_SLEEP_TIME = 1.0  # 60 calls/minute min
CURRENT_SLEEP_TIME = 0.55  # Start conservative

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('category_collection_adaptive.log'),
        logging.StreamHandler()
    ]
)

class AdaptiveCategoryCollector:
    def __init__(self):
        self.api_key = API_KEY
        self.session = requests.Session()
        self.categories = {}
        self.api_calls = 0
        self.start_time = datetime.now()
        self.queue = deque()
        self.processed = set()
        self.should_exit = False
        self.sleep_time = CURRENT_SLEEP_TIME
        self.rate_limit_hits = 0
        self.successful_calls = 0
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown gracefully"""
        logging.info("\nReceived shutdown signal, saving progress...")
        self.should_exit = True
        
    def adjust_rate(self, hit_rate_limit=False):
        """Dynamically adjust sleep time based on rate limit responses"""
        if hit_rate_limit:
            self.rate_limit_hits += 1
            # Increase sleep time by 10%
            self.sleep_time = min(self.sleep_time * 1.1, MAX_SLEEP_TIME)
            logging.info(f"Rate limit hit #{self.rate_limit_hits}, adjusting sleep to {self.sleep_time:.3f}s")
        else:
            self.successful_calls += 1
            # Every 50 successful calls, try to speed up by 5%
            if self.successful_calls % 50 == 0:
                old_sleep = self.sleep_time
                self.sleep_time = max(self.sleep_time * 0.95, MIN_SLEEP_TIME)
                if old_sleep != self.sleep_time:
                    logging.info(f"Speeding up: sleep time now {self.sleep_time:.3f}s")
        
    def save_checkpoint(self):
        """Save current progress"""
        checkpoint = {
            'categories': self.categories,
            'queue': list(self.queue),
            'processed': list(self.processed),
            'api_calls': self.api_calls,
            'timestamp': datetime.now().isoformat(),
            'sleep_time': self.sleep_time,
            'rate_limit_hits': self.rate_limit_hits
        }
        
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        logging.info(f"Checkpoint saved: {len(self.categories)} categories, {len(self.queue)} in queue")
        
    def load_checkpoint(self):
        """Load previous progress if exists"""
        if os.path.exists(CHECKPOINT_FILE):
            logging.info("Loading checkpoint...")
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoint = json.load(f)
            
            self.categories = checkpoint['categories']
            self.queue = deque(checkpoint['queue'])
            self.processed = set(checkpoint['processed'])
            self.api_calls = checkpoint.get('api_calls', 0)
            self.sleep_time = checkpoint.get('sleep_time', CURRENT_SLEEP_TIME)
            self.rate_limit_hits = checkpoint.get('rate_limit_hits', 0)
            
            logging.info(f"Resumed: {len(self.categories)} categories, {len(self.queue)} in queue, sleep={self.sleep_time:.3f}s")
            return True
        return False
        
    def make_api_call(self, endpoint, params=None):
        """Make API call with error handling and adaptive rate limiting"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        params['file_type'] = 'json'
        
        url = f"{BASE_URL}{endpoint}"
        
        for attempt in range(3):  # 3 retries
            try:
                response = self.session.get(url, params=params, timeout=30)
                self.api_calls += 1
                
                if response.status_code == 200:
                    time.sleep(self.sleep_time)  # Adaptive rate limiting
                    self.adjust_rate(hit_rate_limit=False)
                    return response.json()
                elif response.status_code == 429:
                    self.adjust_rate(hit_rate_limit=True)
                    wait_time = 30 + (attempt * 10)  # Progressive backoff
                    logging.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Error {response.status_code}: {response.text[:200]}")
                    return None
            except Exception as e:
                logging.error(f"Exception on attempt {attempt + 1}: {e}")
                time.sleep(5)
        
        return None
    
    def collect_all_categories(self):
        """Recursively collect ALL categories with adaptive rate control"""
        
        # Try to resume from checkpoint
        if not self.load_checkpoint():
            # Start fresh
            logging.info("="*60)
            logging.info("ADAPTIVE CATEGORY HIERARCHY COLLECTION")
            logging.info("="*60)
            
            # Start with root category
            self.queue.append((0, 0))  # (category_id, depth)
        
        save_counter = 0
        
        while self.queue and not self.should_exit:
            cat_id, depth = self.queue.popleft()
            
            if cat_id in self.processed:
                continue
            
            # Get category info
            logging.info(f"Processing category {cat_id} at depth {depth}")
            
            cat_response = self.make_api_call('/category', {'category_id': cat_id})
            if cat_response and 'categories' in cat_response and cat_response['categories']:
                cat_info = cat_response['categories'][0]
            else:
                cat_info = {'id': cat_id, 'name': 'Unknown', 'parent_id': None}
            
            # Get children
            children_response = self.make_api_call('/category/children', {'category_id': cat_id})
            children = children_response.get('categories', []) if children_response else []
            
            # Store category data
            self.categories[str(cat_id)] = {
                'id': cat_id,
                'name': cat_info.get('name', 'Unknown'),
                'parent_id': cat_info.get('parent_id'),
                'depth': depth,
                'children': children,
                'child_ids': [c['id'] for c in children],
                'child_count': len(children),
                'is_leaf': len(children) == 0
            }
            
            # Add children to queue
            for child in children:
                if child['id'] not in self.processed:
                    self.queue.append((child['id'], depth + 1))
            
            self.processed.add(cat_id)
            save_counter += 1
            
            # Save checkpoint every 50 categories
            if save_counter >= 50:
                self.save_checkpoint()
                save_counter = 0
            
            # Progress report
            if len(self.processed) % 50 == 0:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.api_calls / (elapsed / 60) if elapsed > 0 else 0
                effective_rate = 60 / self.sleep_time
                logging.info(f"Progress: {len(self.processed)} categories, {len(self.queue)} in queue, "
                           f"{self.api_calls} API calls, {rate:.1f} calls/min (target: {effective_rate:.1f})")
        
        # Final save
        self.save_checkpoint()
        
        if not self.should_exit:
            # Calculate statistics
            self.calculate_statistics()
            
            # Save complete hierarchy
            self.save_results()
            
            # Clean up checkpoint
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
                logging.info("Removed checkpoint file")
        
        return len(self.categories)
    
    def calculate_statistics(self):
        """Calculate hierarchy statistics"""
        
        stats = {
            'total_categories': len(self.categories),
            'max_depth': 0,
            'categories_by_depth': {},
            'leaf_categories': 0,
            'branch_categories': 0,
            'avg_children_per_branch': 0,
            'rate_limit_hits': self.rate_limit_hits,
            'final_sleep_time': self.sleep_time
        }
        
        total_children = 0
        branch_count = 0
        
        for cat_id, cat_data in self.categories.items():
            depth = cat_data['depth']
            
            # Max depth
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            # Count by depth
            if depth not in stats['categories_by_depth']:
                stats['categories_by_depth'][depth] = 0
            stats['categories_by_depth'][depth] += 1
            
            # Leaf vs branch
            if cat_data['is_leaf']:
                stats['leaf_categories'] += 1
            else:
                stats['branch_categories'] += 1
                total_children += cat_data['child_count']
                branch_count += 1
        
        # Average children
        if branch_count > 0:
            stats['avg_children_per_branch'] = total_children / branch_count
        
        self.stats = stats
    
    def save_results(self):
        """Save complete category hierarchy"""
        
        # Prepare final result
        result = {
            'collection_metadata': {
                'timestamp': datetime.now().isoformat(),
                'api_calls': self.api_calls,
                'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                'categories_collected': len(self.categories),
                'rate_limit_hits': self.rate_limit_hits,
                'final_sleep_time': self.sleep_time
            },
            'hierarchy_statistics': self.stats,
            'categories': self.categories
        }
        
        # Save main file
        filepath = os.path.join(OUTPUT_DIR, 'categories_complete_hierarchy.json')
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        logging.info(f"✅ Saved complete hierarchy to {filepath}")
        
        # Save leaf categories separately (useful for series discovery)
        leaf_categories = {
            cat_id: cat_data 
            for cat_id, cat_data in self.categories.items() 
            if cat_data['is_leaf']
        }
        
        leaf_filepath = os.path.join(OUTPUT_DIR, 'categories_leaf_only.json')
        with open(leaf_filepath, 'w') as f:
            json.dump({
                'leaf_categories': leaf_categories,
                'count': len(leaf_categories),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        logging.info(f"✅ Saved {len(leaf_categories)} leaf categories to {leaf_filepath}")
        
        # Print summary
        logging.info("\n" + "="*60)
        logging.info("COLLECTION COMPLETE")
        logging.info("="*60)
        logging.info(f"Total categories: {len(self.categories)}")
        logging.info(f"Leaf categories: {self.stats['leaf_categories']}")
        logging.info(f"Branch categories: {self.stats['branch_categories']}")
        logging.info(f"Max depth: {self.stats['max_depth']}")
        logging.info(f"API calls made: {self.api_calls}")
        logging.info(f"Rate limit hits: {self.rate_limit_hits}")
        logging.info(f"Final sleep time: {self.sleep_time:.3f}s")
        logging.info(f"Time elapsed: {(datetime.now() - self.start_time).total_seconds():.1f} seconds")
        
        # Print tree structure sample
        logging.info("\nCategories by depth:")
        for depth, count in sorted(self.stats['categories_by_depth'].items()):
            logging.info(f"  Depth {depth}: {count} categories")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    collector = AdaptiveCategoryCollector()
    try:
        collector.collect_all_categories()
    except KeyboardInterrupt:
        logging.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        collector.save_checkpoint()
        sys.exit(1)
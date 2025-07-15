# Project Workspace

## Purpose
This directory serves as a staging area for new project development and cross-agent collaboration before projects are containerized into their own dedicated directories.

## Container Policy
- Each final project gets its own dedicated container directory
- No code should remain at Projects root level long-term
- All projects must be properly containerized for deployment

## Current Project Containers
- `user-dashboard-clean/` - Port 8000 dashboard (Active)
- `user-dashboard-flask-port5001/` - Port 5001 Flask server (Active)

## Usage
- Use this space for initial development and prototyping
- Move completed projects to their own container directories
- Clean up temporary files regularly

## Agent Guidelines
- Data_Analyst: Create analysis projects here, then containerize
- Full_Stack_Software_Engineer: Develop applications here, then containerize  
- Azure_Infrastructure_Agent: Infrastructure tools and scripts here, then containerize

---
*Created: 2025-06-24*  
*Owner: HEAD_OF_ENGINEERING*
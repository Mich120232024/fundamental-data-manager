// Debug volatility calculation

// Vanna-Volga calculation (simplified from the actual implementation)
function calculateVolatility(strike, spot, atmVol, rr, bf, maturity) {
    const forward = spot; // Simplified - no forward adjustment
    const moneyness = Math.log(strike / forward);
    
    // Calculate 25-delta strikes
    const delta = 0.25;
    const volATM = atmVol / 100;
    const sigma_sqrt_t = volATM * Math.sqrt(maturity);
    
    // Approximate 25-delta strikes
    const d2_25 = -0.674; // N^-1(0.25) approximation
    const k_25P = forward * Math.exp(-d2_25 * sigma_sqrt_t + 0.5 * sigma_sqrt_t * sigma_sqrt_t);
    const k_25C = forward * Math.exp(d2_25 * sigma_sqrt_t + 0.5 * sigma_sqrt_t * sigma_sqrt_t);
    
    // Get volatilities from market quotes
    const vol_25P = atmVol + bf - rr/2;
    const vol_25C = atmVol + bf + rr/2;
    
    console.log(`Strike mapping: ${strike.toFixed(4)} vs ATM: ${forward.toFixed(4)}, 25P: ${k_25P.toFixed(4)}, 25C: ${k_25C.toFixed(4)}`);
    console.log(`Vol mapping: ATM: ${atmVol.toFixed(2)}%, 25P: ${vol_25P.toFixed(2)}%, 25C: ${vol_25C.toFixed(2)}%`);
    
    // Vanna-Volga weights
    const x = Math.log(strike / forward);
    const x_25P = Math.log(k_25P / forward);
    const x_25C = Math.log(k_25C / forward);
    const x_ATM = 0;
    
    // Calculate weights
    const w1 = (x - x_ATM) * (x - x_25C) / ((x_25P - x_ATM) * (x_25P - x_25C));
    const w2 = (x - x_25P) * (x - x_25C) / ((x_ATM - x_25P) * (x_ATM - x_25C));
    const w3 = (x - x_25P) * (x - x_ATM) / ((x_25C - x_25P) * (x_25C - x_ATM));
    
    console.log(`Weights: w1=${w1.toFixed(3)}, w2=${w2.toFixed(3)}, w3=${w3.toFixed(3)}, sum=${(w1+w2+w3).toFixed(3)}`);
    
    // Calculate final volatility
    const finalVol = w1 * vol_25P + w2 * atmVol + w3 * vol_25C;
    console.log(`Final vol: ${finalVol.toFixed(2)}%\n`);
    
    return finalVol;
}

// Test with sample data
console.log("=== Testing Volatility Surface Calculation ===\n");

const spot = 1.0833;
const atmVol = 7.64;
const rr = -0.045; // Negative for EUR puts expensive
const bf = 0.158;
const maturity = 1/12; // 1 month

// Test various strikes
const strikes = [1.04, 1.06, 1.08, 1.0833, 1.10, 1.12, 1.14];

console.log("Testing strikes across the smile:");
strikes.forEach(strike => {
    calculateVolatility(strike, spot, atmVol, rr, bf, maturity);
});

// Show expected smile shape
console.log("\n=== Expected Smile Shape ===");
console.log(`Deep OTM Put (0.96): Should be highest (~${(atmVol + bf - rr/2 + 1).toFixed(1)}%)`);
console.log(`25D Put (1.04): ${(atmVol + bf - rr/2).toFixed(2)}%`);
console.log(`ATM (1.0833): ${atmVol}%`);
console.log(`25D Call (1.13): ${(atmVol + bf + rr/2).toFixed(2)}%`);
console.log(`Deep OTM Call (1.20): Should be elevated (~${(atmVol + bf + rr/2 + 0.5).toFixed(1)}%)`);
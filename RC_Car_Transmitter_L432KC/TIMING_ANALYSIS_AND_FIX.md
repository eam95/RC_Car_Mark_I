# RC Car Wireless Communication - Timing Analysis and Fix

## Problem Summary
The transmitter was not receiving data from the RC car when in RECEIVE mode, despite successfully transmitting commands.

## Root Cause: Timing Mismatch

### RC Car (Receiver) Timing - TIM3
- **Prescaler**: 250-1
- **Period**: 65535
- **Clock**: ~100 MHz (H7 APB1)
- **Timer Frequency**: 100 MHz / 250 = 400 kHz
- **Interrupt Period**: 65535 / 400000 = **~164ms**

The RC car checks for incoming commands every **~164ms** in the TIM3 interrupt callback.

### Transmitter Timing - TIM6
- **Prescaler**: 80-1  
- **Period**: 10000
- **Clock**: 80 MHz (L4 system)
- **Timer Frequency**: 80 MHz / 80 = 1 MHz
- **Interrupt Period**: 10000 / 1000000 = **10ms**

The transmitter timer ticks every **10ms** for timeout counting.

### Original Problem
**Transmitter Timeout**: 10 ticks × 10ms = **100ms**
**RC Car Response Time**: Up to **164ms**

**Result**: The transmitter would timeout before the RC car could respond!

## Communication Flow Analysis

### Successful Scenario (After Fix):
```
Time 0ms:     Transmitter sends command → STATE_TRANSMIT
Time 0ms:     Transmitter switches to RX mode → STATE_RECEIVE
Time 0-250ms: Transmitter waits for response (timeout = 250ms)
Time 0-164ms: RC car checks for data (every ~164ms)
Time <164ms:  RC car receives command in TIM3 callback
Time <164ms:  RC car processes command and responds
Time <250ms:  Transmitter receives response ✓
```

### Failed Scenario (Before Fix):
```
Time 0ms:     Transmitter sends command → STATE_TRANSMIT
Time 0ms:     Transmitter switches to RX mode → STATE_RECEIVE
Time 0-100ms: Transmitter waits for response (timeout = 100ms)
Time 100ms:   Transmitter TIMEOUT → STATE_WAIT ✗
Time 164ms:   RC car finally checks for data (too late!)
```

## Solution Applied

### Changed Timeout Period
```c
// OLD: 10 ticks × 10ms = 100ms timeout
if (toggleFlag >= 10)

// NEW: 25 ticks × 10ms = 250ms timeout  
if (toggleFlag >= 25)
```

### Why 250ms?
- RC car checks every ~164ms
- Need buffer for processing time
- 250ms provides safe margin:
  - Worst case: RC car just missed our transmission (0ms)
  - Next check: 164ms later
  - Processing + TX time: ~50ms buffer
  - Total: ~214ms < 250ms ✓

## Additional Improvements Made

1. **Added `nrf24_stop_listen()` on timeout**
   - Ensures NRF24L01 returns to standby mode
   - Prevents stuck RX state

2. **IRQ Pin Support**
   - `HAL_GPIO_EXTI_Callback()` resets timeout when data arrives
   - Allows faster response without polling delay

3. **Status Flag Clearing**
   - `nrf24_clear_rx_dr()` after receiving data
   - Prevents stale data flags

## Testing Recommendations

1. **Monitor LED Patterns**:
   - BLUE: Transmitting command
   - YELLOW: Receiving data from RC car
   - GREEN: Processing UART command
   - OFF: Waiting/idle

2. **Verify Timing**:
   - Send command from UART
   - Should see BLUE LED (TX)
   - Then YELLOW LED within 250ms (RX)
   - Data should appear on UART TX

3. **Test Edge Cases**:
   - Rapid successive commands (< 164ms apart)
   - Delayed RC car response (near 250ms)
   - No RC car (should timeout gracefully)

## NRF24L01 Mode Transition Delays

Per the datasheet, proper delays were added:
- **TX → Standby**: ~130μs (Tpd2stby)
- **Standby → RX**: ~130μs (Tstby2a)
- **Total TX → RX**: ~260μs minimum

The code uses `delay_us(130)` after `nrf24_listen()` to ensure proper mode settling.

## State Machine Overview

```
STATE_WAIT → [UART Command] → STATE_TRANSMIT
STATE_TRANSMIT → [After TX] → STATE_RECEIVE  
STATE_RECEIVE → [Data Received] → STATE_WAIT
STATE_RECEIVE → [Timeout 250ms] → STATE_WAIT
```

## Conclusion

The fix increases the receive timeout from 100ms to 250ms, ensuring the transmitter waits long enough for the RC car to check for commands (~164ms) and respond. This resolves the timing mismatch between the two devices.

The system is now synchronized to handle the RC car's periodic checking interval while maintaining a reasonable timeout for error conditions.

# Testing Guide - RC Car Wireless Communication Fix

## Changes Made

### 1. Increased Receive Timeout
**File**: `RC_Car_Transmitter_L432KC/Core/Src/main.c`

**Change**: Extended timeout from 100ms to 250ms in `HAL_TIM_PeriodElapsedCallback()`
- Old: `if (toggleFlag >= 10)` (10 × 10ms = 100ms)
- New: `if (toggleFlag >= 25)` (25 × 10ms = 250ms)

**Reason**: RC car checks for data every ~164ms, so transmitter needs to wait longer.

### 2. Added Stop Listen on Timeout
**Change**: Added `nrf24_stop_listen()` when timeout occurs
**Reason**: Ensures NRF24L01 returns to standby mode, preventing stuck RX state

## Testing Procedure

### Step 1: Build and Flash
1. Open STM32CubeIDE
2. Build the `RC_Car_Transmitter_L432KC` project
3. Flash the firmware to the L432KC board

### Step 2: Setup Hardware
1. Connect transmitter board to PC via USB
2. Power on RC car (receiver)
3. Ensure both NRF24L01 modules are properly connected
4. Open serial terminal (115200 baud, 8N1)

### Step 3: Test Communication

#### Test 1: Basic Command Send
1. Send command from terminal: `F,30000\r\n` (Forward with PWM 30000)
2. **Expected behavior**:
   - BLUE LED turns on (transmitting)
   - YELLOW LED turns on within 250ms (receiving response)
   - Response data appears in terminal
   - LEDs turn off
   
#### Test 2: Timeout Verification
1. Turn off RC car
2. Send command: `F,30000\r\n`
3. **Expected behavior**:
   - BLUE LED turns on (transmitting)
   - YELLOW LED stays off
   - After ~250ms, transmitter returns to WAIT state
   - No crash or hang

#### Test 3: Rapid Commands
1. Send multiple commands quickly:
   ```
   F,25000\r\n
   R,20000\r\n
   C\r\n
   ```
2. **Expected behavior**:
   - Each command processed sequentially
   - Responses received for each
   - No lost commands

### Step 4: Monitor Timing

Use an oscilloscope or logic analyzer to verify:
1. **Channel 1**: IRQ pin from NRF24L01
2. **Channel 2**: YELLOW LED pin

Verify that YELLOW LED goes high shortly after IRQ pulse.

## LED Indicators

| LED Color | State | Meaning |
|-----------|-------|---------|
| BLUE | ON | Transmitting command to RC car |
| YELLOW | ON | Receiving data from RC car |
| GREEN | ON | Processing UART command from PC |
| OFF | - | Idle/waiting for command |

## Troubleshooting

### Issue: No Response from RC Car

**Check**:
1. RC car powered on?
2. Both devices on same RF channel (90)?
3. RC car's TIM3 interrupt running?
4. RC car in RX_STATE?

**Debug Steps**:
1. Monitor RC car's YELLOW LED (should blink every ~164ms when receiving)
2. Check NRF24L01 connections (CE, CSN, SPI pins)
3. Verify both devices have same address configuration

### Issue: Timeout Every Time

**Possible Causes**:
1. RC car not responding within 250ms
2. RF communication blocked
3. Different channel/address configuration

**Debug Steps**:
1. Increase timeout to 500ms for testing: `if (toggleFlag >= 50)`
2. Add debug output in RC car's TIM3 callback
3. Check RF path (no obstacles, within range)

### Issue: Intermittent Reception

**Possible Causes**:
1. Timing near the edge of 250ms window
2. RC car processing time varies
3. RF interference

**Solutions**:
1. Consider increasing to 300ms: `if (toggleFlag >= 30)`
2. Optimize RC car response time
3. Change RF channel

## Expected Timeline

```
Time (ms)  Event
---------  -----
0          User sends command via UART
0          UART DMA callback triggers
0          STATE_TRANSMIT: Send command via NRF24
1          Switch to RX mode (STATE_RECEIVE)
1          Start timeout counter
0-164      RC car TIM3 fires, checks for data
164        RC car receives command
164        RC car processes and responds
165        Transmitter receives response
165        Parse and send to UART
165        Return to STATE_WAIT
```

**Worst Case**:
- RC car just missed check: 0ms
- Next check: +164ms
- Processing: +10ms
- Total: ~174ms < 250ms ✓

## NRF24L01 Configuration (Both Devices)

Ensure both devices have matching configuration:

```c
- Channel: 90
- Data Rate: 1 Mbps
- TX Power: 0 dBm
- Address Width: 5 bytes
- Payload Size: 32 bytes
- Auto-ACK: Enabled
- CRC: 1 byte
- Auto Retransmit: Delay 4, Count 10
```

## Next Steps / Future Improvements

1. **IRQ-based reception**: Already implemented in `HAL_GPIO_EXTI_Callback()`, can provide faster response
2. **Dynamic timeout**: Adjust based on measured RC car response time
3. **Better error handling**: Retry logic if no response
4. **Status reporting**: Send status back to GUI application
5. **Synchronization pulse**: Send periodic sync to measure round-trip time

## References

- `TIMING_ANALYSIS_AND_FIX.md` - Detailed timing analysis
- RC car code: `rc_car_integrated_I/Core/Src/main.c`
- NRF24L01 datasheet: Section on timing characteristics

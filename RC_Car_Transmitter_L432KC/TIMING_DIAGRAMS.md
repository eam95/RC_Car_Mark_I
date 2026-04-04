# Timing Diagram - Transmitter/Receiver Communication

## Before Fix (100ms Timeout - FAILED)

```
Transmitter Timeline:
┌────────────────────────────────────────────────────────────────────────┐
│ Time:  0ms      10ms     20ms     30ms     ...    100ms    110ms       │
│ ────────┬────────┬────────┬────────┬────────────────┬────────────      │
│         │        │        │        │                │                  │
│ State:  │  TX    │        RX (waiting...)          │  TIMEOUT!        │
│         │        │                                  │  → WAIT          │
│ Flag:   0        1        2        3        ...    10                  │
│         │        │                                  │                  │
│         ▼        ▼                                  ▼                  │
│       Send    Switch                             Give up              │
│       Cmd     to RX                               & stop              │
└────────────────────────────────────────────────────────────────────────┘

RC Car Timeline:
┌────────────────────────────────────────────────────────────────────────┐
│ Time:  0ms                                164ms                        │
│ ────────┬───────────────────────────────────┬───────────────           │
│         │                                   │                          │
│ State:  │         RX (not checking)         │  Check FIFO              │
│         │                                   │  Data found!             │
│         │                                   │  Process & Send          │
│         │                                   │                          │
│         │                                   ▼                          │
│         │                                 ✗ TOO LATE!                  │
│         │                              Transmitter already             │
│         │                              timed out @ 100ms               │
└────────────────────────────────────────────────────────────────────────┘

Result: ✗ NO COMMUNICATION - Timing mismatch!
```

## After Fix (250ms Timeout - SUCCESS)

```
Transmitter Timeline:
┌────────────────────────────────────────────────────────────────────────┐
│ Time:  0ms      10ms     20ms     ...    164ms    174ms    250ms       │
│ ────────┬────────┬────────┬──────────────┬─────────┬────────────      │
│         │        │        │              │         │                  │
│ State:  │  TX    │        RX (waiting...)│  RX     │                  │
│         │        │                       │  Data!  │                  │
│ Flag:   0        1        2        ...  16        17       25         │
│         │        │                       │         │                  │
│         ▼        ▼                       ▼         ▼                  │
│       Send    Switch                   Receive   Process              │
│       Cmd     to RX                    Response  → WAIT               │
└────────────────────────────────────────────────────────────────────────┘

RC Car Timeline:
┌────────────────────────────────────────────────────────────────────────┐
│ Time:  0ms                                164ms    174ms               │
│ ────────┬───────────────────────────────────┬──────┬──────            │
│         │                                   │      │                  │
│ State:  │         RX (not checking)         │Check │ TX               │
│         │                                   │Data  │ Send             │
│         │                                   │found │ Response         │
│         │                                   │      │                  │
│         │                                   ▼      ▼                  │
│         │                                 Receive & Transmit          │
│         │                                 Command   Back              │
└────────────────────────────────────────────────────────────────────────┘

Result: ✓ SUCCESSFUL COMMUNICATION!
```

## Detailed State Machine Flow

### Transmitter State Machine

```
    ┌──────────┐
    │ POWER ON │
    └────┬─────┘
         │
         ▼
    ┌──────────────┐
    │  STATE_WAIT  │◄─────────────────┐
    └────┬─────────┘                  │
         │                            │
         │ UART DMA Rx Complete       │
         │ (Command received)         │
         │                            │
         ▼                            │
  ┌────────────────────┐              │
  │ STATE_TRANSMIT     │              │
  │ - Turn on BLUE LED │              │
  │ - nrf24_transmit() │              │
  │ - nrf24_listen()   │              │
  │ - delay_us(130)    │              │
  │ - toggleFlag = 0   │              │
  └─────┬──────────────┘              │
        │                             │
        ▼                             │
  ┌───────────────────────┐           │
  │ STATE_RECEIVE         │           │
  │ - Turn on YELLOW LED  │           │
  │ - Wait for data       │           │
  │ - Check timeout       │           │
  └─────┬─────────────────┘           │
        │                             │
        │                             │
    ┌───┴────┬────────────────┐       │
    │        │                │       │
    │ Data   │ TIM6           │ Timeout (250ms)
    │ Avail  │ Interrupt      │ toggleFlag >= 25
    │        │ (10ms)         │       │
    ▼        ▼                ▼       │
┌──────┐  ┌──────┐      ┌────────┐   │
│nrf24_│  │toggle│      │nrf24_  │   │
│data_ │  │Flag++│      │stop_   │   │
│avail │  │      │      │listen()│   │
│able()│  │      │      │        │   │
└──┬───┘  │IRQ   │      └────┬───┘   │
   │      │reset │           │       │
   │      │flag? │           │       │
   │      └──────┘           │       │
   │                         │       │
   ▼                         │       │
┌────────────────┐           │       │
│ nrf24_receive()│           │       │
│ Parse data     │           │       │
│ UART transmit  │           │       │
│ Clear RX flag  │           │       │
└────┬───────────┘           │       │
     │                       │       │
     └───────────────────────┴───────┘
```

### RC Car State Machine (Simplified)

```
    ┌──────────┐
    │ POWER ON │
    └────┬─────┘
         │
         ▼
    ┌──────────────┐
    │ nrf24_listen │
    │ Start TIM3   │
    └────┬─────────┘
         │
         ▼
    ┌────────────────────────┐
    │  Main Loop             │
    │  - Execute commands    │◄───┐
    │  - Control motors      │    │
    │  - Read sensors        │    │
    └────────────────────────┘    │
                                  │
         Every ~164ms             │
         TIM3 Interrupt           │
              │                   │
              ▼                   │
    ┌────────────────────┐        │
    │ HAL_TIM_Period     │        │
    │ ElapsedCallback    │        │
    └────┬───────────────┘        │
         │                        │
         ▼                        │
    currentCommMode?              │
         │                        │
    ┌────┴────┬─────────┐         │
    │         │         │         │
RX_STATE  TX_STATE    │         │
    │         │         │         │
    ▼         ▼         │         │
┌─────────┐ ┌─────────┐│         │
│Check    │ │Transmit ││         │
│for data │ │sensor   ││         │
│         │ │data     ││         │
│nrf24_   │ │         ││         │
│data_    │ │Switch   ││         │
│available│ │back to  ││         │
│         │ │RX       ││         │
└────┬────┘ └────┬────┘│         │
     │           │     │         │
     │ Data      │     │         │
     │ found     │     │         │
     ▼           │     │         │
┌─────────────┐  │     │         │
│nrf24_receive│  │     │         │
│Parse command│  │     │         │
│Update state │  │     │         │
│             │  │     │         │
│Set TX mode  │  │     │         │
└────┬────────┘  │     │         │
     │           │     │         │
     └───────────┴─────┴─────────┘
```

## Timing Constants Summary

| Parameter | Value | Calculation |
|-----------|-------|-------------|
| **Transmitter TIM6 Period** | 10ms | (80-1) × 10000 / 80MHz |
| **Transmitter Timeout** | 250ms | 25 ticks × 10ms |
| **RC Car TIM3 Period** | ~164ms | (250-1) × 65535 / 100MHz |
| **NRF24 TX→RX Delay** | 130μs | Tpd2stby + Tstby2a |
| **Safety Margin** | 86ms | 250ms - 164ms |

## Critical Timing Requirements

1. **Transmitter must wait longer than RC car check period**
   - RC car: 164ms
   - Transmitter: 250ms ✓

2. **NRF24L01 mode switching delays must be respected**
   - TX → Standby: ~130μs
   - Standby → RX: ~130μs
   - Code includes: `delay_us(130)` ✓

3. **Interrupt priorities**
   - TIM6 (timeout): Priority 0
   - UART DMA: Priority 0
   - EXTI (IRQ): Priority varies
   - All handled correctly ✓

## Worst-Case Scenarios

### Scenario 1: Just Missed Check
```
Time 0ms:    Transmitter sends command
Time 1ms:    RC car just finished checking (missed by 1ms)
Time 165ms:  RC car checks again, finds command
Time 166ms:  RC car responds
Time 167ms:  Transmitter receives (17th tick)
Status: ✓ PASS (167ms < 250ms)
```

### Scenario 2: Maximum Processing Time
```
Time 0ms:    Transmitter sends command
Time 164ms:  RC car checks, finds command
Time 164ms:  RC car processes (max 50ms)
Time 214ms:  RC car responds
Time 215ms:  Transmitter receives (22nd tick)
Status: ✓ PASS (215ms < 250ms)
```

### Scenario 3: RC Car Not Present
```
Time 0ms:    Transmitter sends command
Time 1-250ms: No response
Time 250ms:  Timeout (25th tick)
Status: ✓ PASS (graceful timeout, returns to WAIT)
```

## RF Signal Timing (NRF24L01)

```
Transmission Phase:
┌───────────────────────────────────────────┐
│ Prepare → SPI Write → RF TX → Wait ACK   │
│ <20μs     <500μs      <500μs   <4ms       │
│                                           │
│ Total: ~5ms maximum                       │
└───────────────────────────────────────────┘

Reception Phase:
┌───────────────────────────────────────────┐
│ RF RX → FIFO Store → IRQ Assert → SPI Rd │
│ <500μs   <10μs       <10μs       <500μs   │
│                                           │
│ Total: ~1ms typical                       │
└───────────────────────────────────────────┘
```

## Conclusion

The 250ms timeout provides adequate margin for:
- RC car's 164ms checking period
- Processing and response time (~10-50ms)
- RF transmission delays (~5-10ms)
- System jitter and variations (~20ms)

**Total expected**: ~164ms + 50ms = 214ms < 250ms ✓

This ensures reliable communication while maintaining reasonable timeout for error conditions.

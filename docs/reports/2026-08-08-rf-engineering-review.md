# RF Engineering Review - MVP Design

**Reviewer:** Rufus RF Engineer (tsayles/homelab)  
**Date:** 2026-08-08  
**Updated:** 2026-08-09 (radio changed to K5PLUS)  
**Project:** Pi Fox Beacon MVP - USB Audio + VOX Mode  
**Branch:** mvp-usb-sound-vox  
**Radio:** Baofeng K5PLUS (10W max, ASIN B0GTDDRGY7)

---

## Review Summary

Overall MVP approach is sound, but several RF considerations need attention for reliable operation and regulatory compliance.

**Radio Specifications:**
- **Model:** Baofeng K5PLUS (tri-band, tri-power)
- **Power:** 10W (HIGH), 7W (MID), 4W (LOW)
- **Bands:** VHF (136-174 MHz), 1.25m (220-260 MHz), UHF (400-480 MHz)
- **Battery:** 2500mAh Li-ion, USB-C + desktop charging
- **Channels:** 999 memory channels
- **Features:** VOX, voice scramble, color LCD, NOAA weather

---

## Key Findings

### 1. FM Carrier Power & Audio Amplitude ✅ (with caveat)

**Finding:** The assumption is **mostly correct** - audio amplitude does NOT directly control PA output power in FM.

**Details:**
- Microphone audio sets **deviation**, not PA wattage
- S-meter readings should be independent of audio level
- **HOWEVER:** Overdrive can cause excessive deviation and splatter
  - Makes signal seem "louder" in recovered audio
  - Widens occupied bandwidth on adjacent channels
  - Can violate FCC bandwidth limits

**Recommendation:** 
- Document deviation limits in MVP guide
- Add "moderate audio level to avoid overdeviation" guidance
- Test actual deviation with service monitor or second receiver

---

### 2. VOX Leading-Edge Clipping ⚠️ (critical issue)

**Finding:** Current design will likely clip the first morse code element.

**Problem:**
- `pre_audio_silence` does NOT help - VOX won't trigger on silence
- VOX needs actual audio signal to key up
- ~100-500ms delay means first dit/dah gets cut off

**Solution:** Add **VOX preamble tone**
- 200-500ms of continuous tone BEFORE first morse character
- Use same frequency as morse code (700-1000 Hz)
- Allows VOX to stabilize and PTT to fully engage
- Discard preamble, keep actual message intact

**Implementation:**
```python
# In morse.py or audio_generator.py
def add_vox_preamble(morse_audio, preamble_ms=300):
    preamble_tone = generate_tone(700, preamble_ms/1000.0)
    return concatenate(preamble_tone, morse_audio)
```

---

### 3. Audio Quality & Deviation ⚠️

**Finding:** APRS-K1 cable and UGREEN adapter may have level/wiring quirks.

**Recommendations:**
- Use single clean tone (700-1000 Hz) - ✅ Already doing this
- Moderate audio level - avoid under/overdriving mic input
- Add **compressor/limiter** or fixed calibration target
- Bench-test actual deviation:
  - Use service monitor if available
  - Or monitor with second receiver + spectrum analyzer
  - Target: ±5 kHz deviation max (standard for narrowband FM)

**Testing checklist:**
- [ ] Measure actual deviation with service monitor
- [ ] Verify no splatter on adjacent channels
- [ ] Confirm morse code is readable (not distorted)
- [ ] Test at different vox_trigger_level settings

---

### 4. VOX Timing Issues ⚠️

**Expected problems:**
- Extra hang time (VOX holds PTT after audio ends)
- Timing jitter (variable VOX trigger delay)
- Possible missed dits (especially at higher WPM)

**Mitigations:**
- Keep WPM moderate (15-20, not 25+)
- Use longer character spacing if needed (Farnsworth timing)
- Add extra `post_audio_silence` for VOX delay compensation
- Test extensively at various VOX sensitivity levels

---

### 5. RF Attenuator for Full Design ✅

**Recommendation:** Use **50Ω switched step attenuator** for full PiTower design.

**Topology:**
- **π or T pads** with relay/FET switching
- Target **1-2 dB steps** over **40-60 dB** total range
- Watch **resistor power dissipation** (at 10W input from K5PLUS)
- Proper **shielding** to avoid RF leakage

**Design notes:**
- Relay-based preferred for 10W power levels
- SMA connectors board-edge mount
- Consider binary-weighted stages (3/6/12/24 dB)
- Existing power dissipation analysis in docs is good foundation

---

### 6. Regulatory Compliance (FCC Part 97) ⚠️

**Requirements:**
- ✅ Station ID every 10 minutes (implemented in beacon.py)
- ✅ Station ID at end of operation (manual Ctrl+C, could be automated)
- ⚠️ Ensure operation on **allowed amateur band** for operator license
- ⚠️ Avoid **excessive deviation** (max occupied bandwidth per Part 97)
- ⚠️ **Unattended/automatic operation** rules:
  - Must have control operator
  - Must be able to terminate transmission remotely
  - Consider remote monitoring/shutdown capability

**Recommendations:**
- Add frequency selection guide (common fox hunt frequencies)
- Document occupied bandwidth testing procedure
- Add remote control/monitoring to Phase 4 roadmap (already planned)
- Consider adding "beacon active" indicator (LED, web status page)

---

## Critical Action Items for MVP

### Before First Transmission:
1. **Add VOX preamble tone** (200-500ms before morse)
2. **Test deviation** with service monitor or second receiver
3. **Verify frequency is legal** for operator's license class
4. **Confirm occupied bandwidth** is within Part 97 limits

### Documentation Updates:
1. Update MVP docs with deviation caveat
2. Add VOX preamble implementation to audio generator
3. Document bench testing procedure for deviation
4. Add regulatory compliance checklist

### Code Updates:
1. Implement VOX preamble in `audio_generator.py` or `morse.py`
2. Add configurable preamble duration to `config.yaml`
3. Update `test_audio.py` to include preamble in test tone
4. Consider adding deviation estimation/warning

---

## Validation Testing Plan

### Bench Tests (Before Field Deployment):
1. **VOX Reliability:**
   - [ ] Test at VOX levels 1-10 on radio
   - [ ] Test at vox_trigger_level 0.3-0.8 in config
   - [ ] Verify first character is NOT clipped
   - [ ] Measure VOX latency (audio start → PTT)
   - [ ] Measure VOX hang time (audio stop → PTT release)

2. **Signal Quality:**
   - [ ] Monitor on second receiver (adjacent freq)
   - [ ] Check for splatter/overdeviation
   - [ ] Verify morse code readability
   - [ ] Test at different audio levels
   - [ ] Spectrum analyzer if available

3. **Regulatory:**
   - [ ] Verify 10-minute ID timing
   - [ ] Confirm frequency is authorized
   - [ ] Check occupied bandwidth < 20 kHz
   - [ ] Test manual emergency shutdown (Ctrl+C)

### Field Tests:
1. **Range Testing:**
   - [ ] Transmit at HIGH (10W) - measure range
   - [ ] Transmit at MID (7W) - measure range
   - [ ] Transmit at LOW (4W) - measure range
   - [ ] Collect S-meter readings at various distances
   - [ ] Verify signal is usable for direction finding

2. **Operational:**
   - [ ] 4-hour continuous operation test
   - [ ] Monitor for timing drift
   - [ ] Check battery consumption (Pi + radio)
   - [ ] Verify beacon stays on frequency

---

## Recommendations for Full PiTower Design

1. **Hardware PTT control:**
   - GPIO → opto-isolator → PTT switch
   - Eliminates VOX latency and clipping issues
   - Precise timing control for morse code

2. **RF Attenuator:**
   - 50Ω switched T-pad or π-pad network
   - 1-2 dB steps, 40-60 dB total range
   - High-power resistors (2W+ at high attenuation for 10W input)
   - Coaxial relays rated for 10W+
   - Proper shielding and SMA connectors

3. **Audio Quality:**
   - I²S audio codec on motherboard HAT
   - Better DAC than generic USB adapter
   - Hardware audio level control
   - Cleaner signal generation

4. **Monitoring:**
   - SWR monitoring (protect against antenna issues)
   - Temperature monitoring (PA transistor)
   - Battery voltage monitoring
   - Status LCD for field operation

---

## Conclusion

The MVP approach is fundamentally sound and will work for fox hunting. The main technical gap is **VOX preamble** to avoid clipping the first character. Secondary concerns are deviation testing and regulatory compliance verification.

**Priority 1 (before first TX):** Add VOX preamble  
**Priority 2 (bench testing):** Measure deviation and bandwidth  
**Priority 3 (documentation):** Update docs with RF considerations  

The full PiTower design with hardware PTT and RF attenuator addresses all the MVP limitations and provides professional-grade beacon functionality.

---

**Signed:** Rufus RF Engineer  
**Reference:** tsayles/homelab/agents/rufus-rf-engineer.agent.md

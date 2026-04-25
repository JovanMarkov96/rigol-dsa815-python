# DSA815 Command Coverage

Status labels: **Implemented**, **Planned**, **Needs-verification**

## Connection / System

| SCPI Command | Status | Method |
|---|---|---|
| `*IDN?` | Implemented | `identify()` |
| `*RST` | Planned | — |
| `*CLS` | Planned | — |

## Frequency (SENSe:FREQuency)

| SCPI Command | Status | Method |
|---|---|---|
| `:SENSe:FREQuency:CENTer` | Implemented | `set_center_frequency()` / `get_center_frequency()` |
| `:SENSe:FREQuency:SPAN` | Implemented | `set_span()` / `get_span()` |
| `:SENSe:FREQuency:STARt` | Implemented | `set_freq_limits()` |
| `:SENSe:FREQuency:STOP` | Implemented | `set_freq_limits()` |

## Bandwidth (SENSe:BANDwidth)

| SCPI Command | Status | Method |
|---|---|---|
| `:SENSe:BANDwidth:RESolution` | Implemented | `set_RBW()` / `get_RBW()` |
| `:SENSe:BANDwidth:VIDeo` | Implemented | `set_VBW()` / `get_VBW()` |

## Sweep (SENSe:SWEep)

| SCPI Command | Status | Method |
|---|---|---|
| `:SENSe:SWEep:TIME` | Implemented | `set_sweep_time()` / `get_sweep_time()` |
| `:SENSe:SWEep:COUNt` | Implemented | `set_sweep_count()` / `get_sweep_count()` |
| `:SENSe:SWEep:POINts?` | Implemented | used internally |

## Initiate

| SCPI Command | Status | Method |
|---|---|---|
| `:INITiate:IMMediate` | Implemented | `initiate_measurement()` |
| `:INITiate:CONTinuous` | Implemented | used internally |
| `:STATus:OPERation:CONDition?` | Implemented | used in sweep-complete polling |

## Trace

| SCPI Command | Status | Method |
|---|---|---|
| `:TRACe:DATA? TRACEn` | Implemented | `measure_trace()`, `get_sweep_data()` |
| `:TRACEn:MODE` | Implemented | `set_trace_mode()` / `get_trace_mode()` |
| `:FORMat:TRACe:DATA` | Implemented | `set_format()` / `get_format()` |

## Input / RF

| SCPI Command | Status | Method |
|---|---|---|
| `:SENSe:POWer:RF:ATTenuation` | Implemented | `set_input_atten()` / `get_input_atten()` |
| `:SENSe:POWer:RF:GAIN:STATe` | Implemented | `enable_RF()` |
| `:OUTput:STATe` | Implemented | `TG_enable()` |
| `:SOURce:POWer:LEVel:IMMediate:AMPLitude` | Implemented | `set_TG_amp()` / `get_TG_amp()` |

## Memory (MMEMory)

| SCPI Command | Status | Method |
|---|---|---|
| `:MMEMory:STORe:TRACe` | Implemented | `save_trace()` |
| `:MMEMory:LOAD:TRACe` | Implemented | `load_trace()` |
| `:MMEMory:STORe:SCReen` | Implemented | `save_screenshot()` |
| `:MMEMory:STORe:SETUp` | Implemented | `save_setup()` |
| `:MMEMory:LOAD:SETUp` | Implemented | `load_setup()` |
| `:MMEMory:STORe:STATe` | Implemented | `save_state()` |
| `:MMEMory:LOAD:STATe` | Implemented | `load_state()` |
| `:MMEMory:DELete` | Implemented | `delete_file()` |
| `:MMEMory:DISK:INFormation?` | Implemented | `get_disk_info()` |
| `:MMEMory:STORe:RESults` | Implemented | `save_results_to_USB()` |

## Marker / Peak search

| SCPI Command | Status | Method |
|---|---|---|
| `:CALCulate:MARKer:PEAK:SEARch:IMMediate` | Planned | — |
| `:CALCulate:MARKer:X?` | Planned | — |
| `:CALCulate:MARKer:Y?` | Planned | — |

## Limit lines

| SCPI Command | Status | Method |
|---|---|---|
| `:CALCulate:LIMit` subsystem | Planned | — |

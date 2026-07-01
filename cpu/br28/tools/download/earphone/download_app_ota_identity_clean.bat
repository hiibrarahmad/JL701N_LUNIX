@echo off

cd %~dp0

copy ..\..\script.ver .
copy ..\..\tone.cfg .
copy ..\..\p11_code.bin .
copy ..\..\br28loader.bin .
copy ..\..\ota.bin .
copy ..\..\anc_coeff.bin .
copy ..\..\anc_gains.bin .

@REM For identity updates, force full erase so CFG/VM are definitely refreshed.
..\..\isd_download.exe ..\..\isd_config.ini -tonorflash -dev br28 -boot 0x120000 -div8 -wait 300 -uboot ..\..\uboot.boot -app ..\..\app.bin -res ..\..\cfg_tool.bin tone.cfg p11_code.bin ..\..\eq_cfg_hw.bin -uboot_compress -format all

..\..\ufw_maker.exe -fw_to_ufw jl_isd.fw
copy jl_isd.ufw update.ufw
del jl_isd.ufw

if exist script.ver del script.ver
if exist tone.cfg del tone.cfg
if exist p11_code.bin del p11_code.bin
if exist br28loader.bin del br28loader.bin
if exist anc_coeff.bin del anc_coeff.bin
if exist anc_gains.bin del anc_gains.bin

ping /n 2 127.1>null
IF EXIST null del null

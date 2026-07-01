



















##!/bin/sh


cd "$(dirname "$0")"


chmod +x isd_download fw_add 2>/dev/null

${OBJDUMP} -D -address-mask=0x7ffffff -print-imm-hex -print-dbg -mcpu=r3 $1.elf > $1.lst
${OBJCOPY} -O binary -j .text $1.elf text.bin
${OBJCOPY} -O binary -j .data $1.elf data.bin
${OBJCOPY} -O binary -j .moveable_slot $1.elf mov_slot.bin
${OBJCOPY} -O binary -j .data_code $1.elf data_code.bin
${OBJCOPY} -O binary -j .overlay_aec $1.elf aec.bin
${OBJCOPY} -O binary -j .overlay_aac $1.elf aac.bin
${OBJCOPY} -O binary -j .psr_data_code $1.elf psr_data_code.bin

${OBJDUMP} -section-headers -address-mask=0x7ffffff $1.elf
${OBJSIZEDUMP} -lite -skip-zero -enable-dbg-info $1.elf | sort -k 1 > symbol_tbl.txt

cat text.bin data.bin mov_slot.bin data_code.bin aec.bin aac.bin psr_data_code.bin > app.bin
cp eq_cfg_hw_less.bin eq_cfg_hw.bin
if [ -x "/opt/utils/strip-ini" ] && [ -s "/opt/utils/strip-ini" ]; then
    /opt/utils/strip-ini -i isd_config.ini -o isd_config.ini
else
    sed -i '/^[[:space:]]*[;#]/d; /^[[:space:]]*$/d' isd_config.ini
fi

./isd_download isd_config.ini -tonorflash -dev br28 -boot 0x120000 -div8 -wait 300 -uboot uboot.boot -app app.bin -res cfg_tool.bin tone.cfg p11_code.bin eq_cfg_hw.bin -uboot_compress -format vm

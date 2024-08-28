# PETER
Peripheral ECP5 Technology and Entertainment Resource

## Description
Peter is an FPGA board based around a Lattice ECP5 FPGA chip. It provides peripheral features for a plug in 3.3V RCBUS CPU card. PETER provides video, audio, I2C, SPI, SNES controller, 2x USB UART, and PS2 keyboard and mouse connection to a Retro computer RCBUS. In addition there is an ESP32-S3 Wifi module for programming the FPGA and bootloader(s), Zilog ZDI, WiFi console and additonal features. There are on-board connectors for provision of a W5500 Wizmon Ethernet module and DS3132 Real Time Clock + AT24C32 EEPROM module.

## Top View
![PETER Top View Board Image](output/PETER_V0_3d_Top.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Front View
![PETER Front View Board Image](output/PETER_V0_3d_Front.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Rear View
![PETER Rear View Board Image](output/PETER_V0_3d_Rear.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Side View
![PETER Side View Board Image](output/PETER_V0_3d_Side.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Board Bring-up Status
   - Most of the board has been tested and status is okay.
   - Audio RTL on the FPGA has yet to be implmented so the audio port is not tested.
   - The ESP32 SD card slot has not been tested.

## Programming
1. To program the FPGA FLASH you can use a FT232H module.
   - Method (1) uses the open source ecpprog tool and JTAG. 
   - Pin connections are as follows:

| Signal        |  FT232H Module Pin  | PETER Location |
| ------------- | ------------------- | ---------------- |
| TDI           | AD1 | J601.2 |
| TMS           | AD3 | J601.4 |
| TCK           | AD0 | J601.8 |
| TDO           | AD2 | J601.10 |
| GND      | Module Specific | J503.1 or 3,5,6,7,9 |

   - Method (2) uses an open source SPI programmer. 
   - Pin connections are as follows:

| Signal        |  FT232H Module Pin  | PETER Location |
| ------------- | ------------------- | ---------------- |
| SPI_CLK       | AD0 | J602.8 |
| SPI_MOSI      | AD1 | J602.2 |
| SPI_MISO      | AD2 | J602.10 |
| SPI_CS_N      | AD3 | J602.4 |
| CRESET/INIT_N | AD4 | J602.6 |
| DONE          | AD5 | J602.5 |
| GND      | Module Specific | J602.1, or 3,7,9 |

   - Connector pin layout has been chosen so that the same programming cable is capable SPI and JTAG.

2. The ESP32 is programmed using the J1202 USB connector in JTAG mode. Alternatively it can be programmed over ESP32 UART0 on pins J1105.11 and J1105.12. When using UART switch S1201 provides the 'boot' function to put the ESP32 into programming mode. USB JTAG does not require the boot switch. Both methods require use of ESP32 programming tool found in Arduino, Platform IO, or Esspressif SW tools.

## PETER Board Rev 0.0 Release Notes

1. The 'output' directory contains the BOM, netlist, and PDF schematic.

2. Board design used KiCad 8.0.4.

3. There are only four mounting holes. If the RCBUS card slot is used the board should be supported when plugging in the card.

4. Silkscreen error
   - J1106 silkscreen should show GPIO. Instead silkscreen shows USER I2C SPI.
   - J1101 silkscreen should show USER I2C SPI. Instead silkscreen shows GPIO.

5. USB Uart TX/RX LED's are rather weak compared to other LED's. May want to change resistor to lower value (eg 270ohms)?
   - R1001, R1002, R1007, R1008.
   - Note : in general the LED's are low light by design.

6. R401 should be 10K instead of 0 ohms if R401 is populated.

7. Reset signal FPGA_CRESET_N high = 2.77V due to being open drain and Q604 having 20K biasing resistance. This meets the 2V Vih requirement of the FPGA pin. If a higher level is desired change R617 to 1K.

8. The SRAM memory MEM_WE_N, MEM_OE_N, and MEM_CE_N signals are rounted through the FPGA and as a consequence there is about a ~10ns delay from CPU_WR_N, CPU_RD_N, CPU_MREQ_N signals. If direct connection is needed The RCBUS board can be designed to directly connect to the SRAM memory signals. Alternatively the RCBUS expansion connector provides pins where jumper wires can be attached.

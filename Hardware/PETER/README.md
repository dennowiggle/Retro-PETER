# PETER
Peripheral ECP5 Technology and Entertainment Resource

## Description
PETER is an FPGA board based around a Lattice ECP5 FPGA chip. It provides peripheral features for a plug in 3.3V RCBUS CPU card. 

The PETER board provides video, audio, I2C, SPI, SNES controller, 2x USB UART, and PS2 keyboard and mouse connection to a 3.3V RCBUS card slot and expansion connector. 

In addition there is an ESP32-S3 WiFi module for programming the FPGA and system bootloader(s), Zilog ZDI, WiFi console and additonal features. There are on-board connectors for provision of a W5500 Wizmon Ethernet module and DS3132 Real Time Clock + AT24C32 EEPROM module.

**Warning** : This is a 3.3V system and any connections to PETER, including RCBUS, must NOT exceed 3.3V.

**Disclaimer** : This is a hobby project and a vehicle for play. Not intended to be a product or to be optimised for size, cost, function, or meet any standard. All boards are prototypes and should be considered such even if there are new revisions over time.

## Top View
![PETER Top View Board Image](output/PETER_V0_3d_Top.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Front View
![PETER Front View Board Image](output/PETER_V0_3d_Front2.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Rear View
![PETER Rear View Board Image](output/PETER_V0_3d_Rear2.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Side View
![PETER Side View Board Image](output/PETER_V0_3d_Side.jpg "Top View of the Peripheral ECP5 Technology and Entertainment Resource board.")

## Board Bring-up Status
   - Most of the board has been tested and status is okay.
   - Audio RTL on the FPGA has yet to be implmented so the audio port is not tested.
   - The ESP32 SD card slot has not been tested.
   - RCBUS compatibility is 3.3V and has not been tested with any RCBUS supported products other than the boards here.

## Programming
* To program the FPGA FLASH an FT232H USB module can be used.
   1. Method (1) uses the open source `ecpprog` tool and JTAG. 
       - Pin connections are as follows:

      | Signal        |  FT232H Module Pin  | PETER Location |
      | ------------- | ------------------- | ---------------- |
      | TDI           | AD1 | J601.2 |
      | TMS           | AD3 | J601.4 |
      | TCK           | AD0 | J601.8 |
      | TDO           | AD2 | J601.10 |
      | GND      | Module Specific | J503.1 or 3,5,7,9 |

   2. Method (2) uses an open source SPI programmer SW tool. 
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

   - Connector pin layout has been chosen so that the same programming cable supports both SPI and JTAG.

* The on-board ESP32 module is programmed using the J1202 USB connector in JTAG mode. 
   - Alternatively it can be programmed over ESP32 UART0 on pins J1105.11 and J1105.12. 
   - When using UART switch S1201 provides the 'boot' function to put the ESP32 into programming mode. 
   - USB JTAG does not require the boot switch. 
   - Both methods require use of the ESP32 programming tool found in Arduino, Platform IO, or Espressif SW tools.

## PETER Board Rev 0.0 Release Notes

1. The 'output' directory contains the BOM, netlist, and PDF schematic.

2. Board design used KiCad 8.0.4.

3. There are only four mounting holes. If the RCBUS card slot is used the board should be supported from underneath when plugging in the card to prevent the PCB from bending. Adhesive rubber feet may be a better option than using the mounting holes.

4. Silkscreen error
   - J1106 silkscreen should show `GPIO`. Instead silkscreen shows `USER I2C SPI`.
   - J1101 silkscreen should show `USER I2C SPI`. Instead silkscreen shows `GPIO`.

5. USB UART TX/RX LED's are rather weak compared to the other LED's on the board. The resistor in series with each LED can be changed to a lower value (eg 270ohms).
   - Resistor locations are R1001, R1002, R1007, R1008.
   - Note : in general the LED's are low light by design. This is intentional.

6. R401 should be 10K instead of 0 ohms if R401 is populated.

7. J301 RCBUS expansion connector part number was changed to PH2RA-80-UA which has a gold flash plating providing less resistance during plug/unplug. 

8. J302 RCBUS card slot socket was purchased from Ebay and had gold plating. 

9. Reset signal FPGA_CRESET_N high level = 2.77V due to being open drain and Q604 having 20K biasing resistance. This meets the 2V Vih requirement of the FPGA pin. If a higher level is desired change R617 to 1K.

10. The SRAM memory MEM_WE_N, MEM_OE_N, and MEM_CE_N signals are routed through the FPGA and as a consequence there is about a ~10ns delay from the CPU_WR_N, CPU_RD_N, CPU_MREQ_N signals to their SRAM equivalent signals. 
    - If direct connection is needed for timing needs then the RCBUS board can be designed to directly connect to the SRAM memory signals. Alternatively the RCBUS expansion connector provides pins where jumper wires can be attached.

11. The [FTDI DT_PROG](https://www.ftdichip.com/Support/Documents/AppNotes/AN_124_User_Guide_For_FT_PROG.pdf) tool can be used to program U1001 & U1002 FT230X pin CBUS3 for VBUS_SENSE function. 
    - This allows the FT230X IC to detect removal of the USB cable and resets the USB connection without a power cycle of the board.

12. U202 and U203 TPS62A02PDDCR used for the 3.3V and 1.1V power supplies is a 2A part. The system is low power and the 1A TPS62A01PDDCR should be sufficient and would provide a lower overcurrent trip point providing enhanced overcurrent protection. The 1A part is footprint and circuit compatible.
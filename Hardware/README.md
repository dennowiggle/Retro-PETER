# Retro-PETER Hardware Design Files
A Retro Computer project => FPGA peripheral board + 3.3V RCBUS slot + CPU board(s) making a custom system.

Hardware design files in KiCad 8 format are located here. 

Schematic design PDF drawings can be found in the `output` sub-directory of each board directory.

**Warning** : This is a 3.3V system and any connections to PETER, including RCBUS, must NOT exceed 3.3V.

**Disclaimer** : This is a hobby project and a vehicle for play. Not intended to be a product or to be optimised for size, cost, function, or meet any standard. All boards are prototypes and should be considered such even if there are new revisions over time.

## Description
Retro-PETER is a family of boards based around the Lattice ECP5 FPGA to create a custom retro computer system.
* [PETER](PETER "Peripheral ECP5 Technology and Entertainment Resource board.") base board with FPGA provides the peripheral features. It has on board SRAM memory but no CPU.
    - One 3.3V RCBUS connector provides a CPU slot.
    - One 3.3V RCBUS expansion connector allows connection of an RCBUS backplane for more card slots.
* [ANALYZER](Analyzer "Logic Analyzer for RCBUS using PI PICO 2") is a 5V tolerant 72 channel logic analyzer for RCBUS.
* [BALD](BALD "Bus Activity LED Display.") is an RCBUS LED card that flickers lights when there is activity. I found this useful for bringup of new CPU's either on an RCBUS CPU card or internal CPU cores.
* [BUTLER](BUTLER "Backplane with Universal Translation Logic for Exploring Retro") is a backplane with voltage translation logic to support 2 x 3.3V connectors for 3.3V RCBUS cards and 2 x 5V connectors for 5V RCBUS cards.
* [GOLD](GOLD "GPIO On LED Display.") is a simple LED board that connects to 6 GPIO outputs for flashing lights and debug info. I love a binary counter.
* [RANDY](RANDY "RCBUS Adapter to Nouveau Design. Yeah!") is a bus adapter from RCBUS to John's Basement [2067-Z8S180](https://github.com/johnwinans/2067-Z8S180/) card.
* [SEWER](SEWER "Simple Eval With EZ80F91 on RCBUS") is an eZ80 CPU card.
* [SPIFEE](SPIFEE "Sixty-eight thousand Processor Including Flash Engineering Eval") is an RCBUS board with an M68SEC000FU20 CPU that runs in 8-bit mode.
* [ZORO](ZORO "Z8S180 On RCBUS Only.") is a Z180 RCBUS CPU card.


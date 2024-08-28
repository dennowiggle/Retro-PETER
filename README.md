# Retro-PETER
A Retro computer project => FPGA peripheral board + RCBUS + CPU board(s) making a custom system.

## Description
Retro-PETER is a family of boards based around the Lattice LFEU-25F-7TG144 FPGA to create a custom retro system.
* [PETER](Hardware/PETER "Peripheral ECP5 Technology and Entertainment Resource board.") base board with FPGA provides the peripheral features. It has on board SRAM memory but no CPU.
    - One 3.3V RCBUS connector provides a CPU slot.
    - One 3.3V RCBUS expansion connector allows connection of an RCBUS backplane for more cards.
* [GOLD](Hardware/GOLD "GPIO On LED Display.") is a simple LED board that connects to 6 GPIO outputs for flashing lights and debug info. I love a binary counter.
* [BALD](Hardware/BALD "Bus Activity LED Display.") is an RCBUS LED card that flickers lights when there is activity. I found this useful for bringup of new CPU's either on an RCBUS CPU card or internal CPU cores.
* [RANDY](RANDY "RCBUS Adapter to Nouveau Design. Yeah!") is a bus adapter from RCBUS to John's Basement 2067-Z8S180 card.
* [ZORO](ZORO "Z8S180 On RCBUS Only.") is a Z180 RCBUS CPU card.
* [SEWER](SEWER "Simple Eval With EZ80F91 on RCBUS") is an eZ80 CPU card.

## Background
John Winans has a video series and boards for an ice40HX4K + Z180 CPU card. This project grew from following along with those video's and projects. You can follow John's work:
* [John's Basement FPGA series](https://www.youtube.com/playlist?list=PL3by7evD3F52On-ws9pcdQuEL-rYbNNFB).
    - [Supporting ice40HX4K board](https://github.com/johnwinans/2057-ICE40HX4K-TQ144-breakout).
    - [Code for Series](https://github.com/johnwinans/Verilog-Examples).
* [John's Basement Z80 Nouveau series](https://www.youtube.com/playlist?list=PL3by7evD3F52rUbThUNDYGxNpKFF1HCNT).
- [Supporting Z8S180 board](https://github.com/johnwinans/2057-ICE40HX4K-TQ144-breakout).
    - [Code for Series](https://github.com/johnwinans/2067-Z8S180/tree/main/fpga).
* [Johns Z80 Retro!](https://discord.gg/g8UJeMXs) Discord channel.


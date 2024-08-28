# Retro-PETER
A Retro computer project => FPGA peripheral board + 3.3V RCBUS slot + CPU board(s) making a custom system.

## Description
Retro-PETER is a family of boards based around the Lattice ECP5 FPGA to create a custom retro computer system.
* [PETER](Hardware/PETER "Peripheral ECP5 Technology and Entertainment Resource board.") base board with FPGA provides the peripheral features. It has on board SRAM memory but no CPU.
    - One 3.3V RCBUS connector provides a CPU slot.
    - One 3.3V RCBUS expansion connector allows connection of an RCBUS backplane for more card slots.
* [GOLD](Hardware/GOLD "GPIO On LED Display.") is a simple LED board that connects to 6 GPIO outputs for flashing lights and debug info. I love a binary counter.
* [BALD](Hardware/BALD "Bus Activity LED Display.") is an RCBUS LED card that flickers lights when there is activity. I found this useful for bringup of new CPU's either on an RCBUS CPU card or internal CPU cores.
* [RANDY](Hardware/RANDY "RCBUS Adapter to Nouveau Design. Yeah!") is a bus adapter from RCBUS to John's Basement [2067-Z8S180](https://github.com/johnwinans/2067-Z8S180/) card.
* [ZORO](Hardware/ZORO "Z8S180 On RCBUS Only.") is a Z180 RCBUS CPU card.
* [SEWER](Hardware/SEWER "Simple Eval With EZ80F91 on RCBUS") is an eZ80 CPU card.

**WARNING** : This is a 3.3V system and any connections to PETER, including RCBUS, must NOT exceed 3.3V.

**Disclaimer** This is a hobby project and a vehicle for play. Not intended to be a product or to be optimised for size, cost, function, or meet any standard. All boards are prototypes and should be considered such even if there are new revisions over time.

## Background
John Winans has a video series and boards for an ice40HX4K + Z180 CPU card aka Z80 Nouveau. There is also a companion CP/M video series and project files. This project grew from following along with those video's and projects. Here are some links to follow John's work :
* John's Basement [FPGA](https://www.youtube.com/playlist?list=PL3by7evD3F52On-ws9pcdQuEL-rYbNNFB) YouTube series.
    - Supporting  [2057-ice40HX4K](https://github.com/johnwinans/2057-ICE40HX4K-TQ144-breakout) board.
    - [Code](https://github.com/johnwinans/Verilog-Examples) for Series.
* John's Basement [Z80 Nouveau](https://www.youtube.com/playlist?list=PL3by7evD3F52rUbThUNDYGxNpKFF1HCNT) YouTube series.
    - Supporting [2067-Z8S180](https://github.com/johnwinans/2067-Z8S180/) board.
    - [Code](https://github.com/johnwinans/2067-Z8S180/tree/main/fpga) for Series.
* John's Basement [Z80 Retro](https://www.youtube.com/playlist?list=PL3by7evD3F51Cf9QnsAEdgSQ4cz7HQZX5) YouTube series covering CP/M.
    - [CP/M SW](https://github.com/Z80-Retro/2063-Z80-cpm) to go along wuth the video series and which supports 2057-ice40HX4K + 2067-Z8S180 aka Z80 Nouveau.
* Johns Z80 Retro! [Discord](https://discord.gg/jf73DRZvh5) channel.

from pchip16 import cpu
import sure
import random
from mock import Mock


def test_little_endianess():
    chip16 = cpu.Cpu()

    chip16.write_16bit(0x0000, 0x00AA)

    chip16.read_8bit(0x0000).should.eql(0x00AA)
    chip16.read_8bit(0x0001).should.eql(0x0000)

    hex(chip16.read_8bit(0x0000)).should.eql("0xaa")

def test_program_counter():
    chip16 = cpu.Cpu()

    chip16.pc = 0xCAFE

    chip16.pc.should.eql(0xCAFE)

def test_stack_pointer():
    chip16 = cpu.Cpu()

    chip16.sp = 0xCAFE

    chip16.sp.should.eql(0xCAFE)

def test_write_and_read():
    chip16 = cpu.Cpu()

    cafe = 0xCAFE

    chip16.write_16bit(0x0000, cafe)

    chip16.read_8bit(0x0000).should.eql(0xFE)
    chip16.read_8bit(0x0001).should.eql(0xCA)
    chip16.read_16bit(0x0000).should.eql(0xCAFE)

def test_general_registers():
    chip16 = cpu.Cpu()

    for r in range(0x0,0xF):
        chip16.r[r] = 0x00FA

    chip16.r[0x0].should.eql(0x00FA)
    chip16.r[0xF-1].should.eql(0x00FA)

def test_create_params():
    # 40 YX LL HH
    chip16 = cpu.Cpu()

    op_code = 0x40
    yx = 0b00010010 #y=1, x=2
    ll = 0b00000001
    hh = 0b00000010

    chip16.write_8bit(0x0000, op_code)
    chip16.write_8bit(0x0001, yx)
    chip16.write_8bit(0x0002, ll)
    chip16.write_8bit(0x0003, hh)

    params = chip16.create_params(0x0000)

    params['op_code'].should.eql(0x40)
    params['x'].should.eql(2)
    params['y'].should.eql(1)
    params['ll'].should.eql(1)
    params['hh'].should.eql(2)
    params['hhll'].should.eql(0b0000001000000001)

def test_STM_RX():
    # STM RX, HHLL
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x30) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand

    chip16.r[0x0] = 0xBABE
    chip16.write_16bit(0xAAFF, 0xF00D)

    chip16.step()

    chip16.read_16bit(0xAAFF).should.eql(0xBABE)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_STM_RX_RY():
    # STM RX, RY
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x31) #op code
    chip16.write_8bit(initial_address + 1, 0b00110000) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand

    chip16.r[0] = 0xAAAA
    chip16.r[3] = 0x0007
    chip16.write_16bit(0x0007, 0x1010)

    chip16.step()

    chip16.read_16bit(0x0007).should.eql(0xAAAA)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_LDI_RX():
    # LDI RX, HHLL
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x20) #op code
    chip16.write_8bit(initial_address + 1, 0b00010000) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand

    chip16.step()

    chip16.r[0x00].should.eql(0xAAFF)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_LDI_SP():
    # LDI SP, HHLL
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x21) #op code
    chip16.write_8bit(initial_address + 1, 0b00010000) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand

    chip16.step()

    chip16.sp.should.eql(0xAAFF)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_LDM_RX():
    # LDM RX, HHLL
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x22) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand
    chip16.write_8bit(0xAAFF, 0xCC) # value for address pointed by hhll
    chip16.write_8bit(0xAB00, 0xAB) # value for address pointed by hhll

    chip16.step()

    chip16.r[0b0010].should.eql(0xABCC)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_LDM_RX_RY():
    # LDM RX, RY - Set RX to [RY].
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x23) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xFF) #ll operand
    chip16.write_8bit(initial_address + 3, 0xAA) #hh operand

    chip16.r[0b0010] = 0xAB
    chip16.r[0b0001] = 0xCD
    chip16.write_8bit(0x00CD, 0xEF)
    chip16.write_8bit(0x00CE, 0xBE)

    chip16.step()

    chip16.r[0b0010].should.eql(0xBEEF)
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_NOP():
    # NOP - No operation.
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x00) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x00) #ll operand
    chip16.write_8bit(initial_address + 3, 0x00) #hh operand

    chip16.step()

    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_CLS():
    # CLS - Clear FG, BG = 0.
    gpu = Mock()
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x01) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x00) #ll operand
    chip16.write_8bit(initial_address + 3, 0x00) #hh operand

    chip16.step()

    gpu.clear_fg.assert_called_once()
    gpu.clear_bg.assert_called_once()
    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_VBLNK_when_it_is_disable():
    # VBLNK - Wait for VBlank. If (!vblank) PC -= 4.
    gpu = Mock()
    gpu.vblank = Mock(return_value=False)
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x02) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x00) #ll operand
    chip16.write_8bit(initial_address + 3, 0x00) #hh operand

    chip16.step()

    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address)

def test_VBLNK_when_it_is_enable():
    # VBLNK - Wait for VBlank. If (!vblank) PC -= 4.
    gpu = Mock()
    gpu.vblank = Mock(return_value=True)
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x02) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x00) #ll operand
    chip16.write_8bit(initial_address + 3, 0x00) #hh operand

    chip16.step()

    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)

def test_BGC():
    # BGC N - Set background color to index N (0 is black).
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x03) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0b00000100) #ll operand
    chip16.write_8bit(initial_address + 3, 0x00) #hh operand

    chip16.step()

    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)
    chip16.gpu.bg.should.eql(0b0100)

def test_SPR():
    # SPR HHLL - Set sprite width (LL) and height (HH).
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x04) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x21) #ll operand
    chip16.write_8bit(initial_address + 3, 0x42) #hh operand

    chip16.step()

    chip16.current_cyles.should.eql(1)
    chip16.pc.should.eql(initial_address + 4)
    chip16.gpu.spritew.should.eql(0x21)
    chip16.gpu.spriteh.should.eql(0x42)

def test_DRW_HHLL_with_no_overlaps():
    # Draw sprite from address HHLL at (RX, RY).
    gpu = Mock()
    gpu.there_is_overlap = Mock(return_value=False)
    gpu.drw_hhll = Mock(return_value=0)
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x05) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x21) #ll operand
    chip16.write_8bit(initial_address + 3, 0x42) #hh operand

    chip16.r[0b0001] = 0x10 #y
    chip16.r[0b0010] = 0x20 #x

    chip16.step()

    gpu.drw_hhll.assert_called_once_with(0x4221, 0x20, 0x10)
    chip16.flag_carry.should.eql(0x0)

def test_DRW_HHLL_with_overlaps():
    # Draw sprite from address HHLL at (RX, RY).
    gpu = Mock()
    gpu.there_is_overlap = Mock(return_value=True)
    gpu.drw_hhll = Mock(return_value=1)
    chip16 = cpu.Cpu()
    chip16.flag_carry = 0x0
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x05) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x21) #ll operand
    chip16.write_8bit(initial_address + 3, 0x42) #hh operand

    chip16.r[0b0001] = 0x10 #y
    chip16.r[0b0010] = 0x20 #x

    chip16.step()

    gpu.drw_hhll.assert_called_once_with(0x4221, 0x20, 0x10)
    chip16.flag_carry.should.eql(0x1)

def test_DRW_RZ_with_no_overlaps():
    # Draw sprite from [RZ] at (RX, RY).
    gpu = Mock()
    gpu.there_is_overlap = Mock(return_value=False)
    gpu.drw_rz = Mock(return_value=0)
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x06) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll operand
    chip16.write_8bit(initial_address + 3, 0x42) #hh operand

    chip16.r[0b0001] = 0x10 #y
    chip16.r[0b0010] = 0x20 #x
    chip16.r[0b0011] = 0x4000 #z => pointing to address 0x4000

    chip16.write_8bit(0x4000, 0xAA)
    chip16.write_8bit(0x4001, 0xBB)

    chip16.step()

    # we need to compare both using 2's complement
    gpu.drw_rz.assert_called_once_with(0xBBAA, 0x20, 0x10)
    chip16.flag_carry.should.eql(0x0)

def test_DRW_RZ_with_overlaps():
    # Draw sprite from [RZ] at (RX, RY).
    gpu = Mock()
    gpu.there_is_overlap = Mock(return_value=True)
    gpu.drw_rz = Mock(return_value=1)
    chip16 = cpu.Cpu()
    chip16.gpu = gpu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x06) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll operand
    chip16.write_8bit(initial_address + 3, 0x42) #hh operand

    chip16.r[0b0001] = 0x10 #y
    chip16.r[0b0010] = 0x20 #x
    chip16.r[0b0011] = 0x4000 #z => pointing to address 0x4000

    chip16.write_8bit(0x4000, 0xAA)
    chip16.write_8bit(0x4001, 0xBB)

    chip16.step()

    # we need to compare both using 2's complement
    gpu.drw_rz.assert_called_once_with(0xBBAA, 0x20, 0x10)
    chip16.flag_carry.should.eql(0x1)

def test_RND():
    # RND RX, HHLL - Store random number in RX (max. HHLL).
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x07) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x10) #ll operand
    chip16.write_8bit(initial_address + 3, 0x01) #hh operand

    chip16.write_8bit(initial_address + 4, 0x07) #op code
    chip16.write_8bit(initial_address + 5, 0b00010010) #x,y index operand
    chip16.write_8bit(initial_address + 6, 0x05) #ll operand
    chip16.write_8bit(initial_address + 7, 0x00) #hh operand

    chip16.step()

    chip16.r[0b0010].should.be.lower_than_or_equal_to(0x110)

    chip16.step()

    chip16.r[0b0010].should.be.lower_than_or_equal_to(0x5)

def test_FLIP():
    # FLIP [0|1], [0|1] - Set hflip = [false|true], vflip = [false|true]
    chip16 = cpu.Cpu()
    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x08) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x0) #ll operand
    chip16.write_8bit(initial_address + 3, 0b00) #hh operand

    chip16.step()

    chip16.gpu.hflip.should.be.falsy
    chip16.gpu.vflip.should.be.falsy

    chip16.write_8bit(initial_address + 4, 0x08) #op code
    chip16.write_8bit(initial_address + 5, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 6, 0x0) #ll operand
    chip16.write_8bit(initial_address + 7, 0b01) #hh operand

    chip16.step()

    chip16.gpu.hflip.should.be.falsy
    chip16.gpu.vflip.should.be.truthy

    chip16.write_8bit(initial_address + 8, 0x08) #op code
    chip16.write_8bit(initial_address + 9, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 10, 0x0) #ll operand
    chip16.write_8bit(initial_address + 11, 0b11) #hh operand

    chip16.step()

    chip16.gpu.hflip.should.be.truthy
    chip16.gpu.vflip.should.be.truthy

def test_SND0():
    # Stop playing sounds.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x09) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0x0) #ll operand
    chip16.write_8bit(initial_address + 3, 0x0) #hh operand

    chip16.step()

    spu.stop.assert_called_once()

def test_SND1():
    # Play 500Hz tone for HHLL ms.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x0A) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xBB) #ll operand
    chip16.write_8bit(initial_address + 3, 0x10) #hh operand

    chip16.step()

    spu.play500hz.assert_called_once_with(0x10BB)

def test_SND2():
    # Play 1000Hz tone for HHLL ms.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x0B) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xBB) #ll operand
    chip16.write_8bit(initial_address + 3, 0x10) #hh operand

    chip16.step()

    spu.play1000hz.assert_called_once_with(0x10BB)

def test_SND3():
    # Play 1500Hz tone for HHLL ms.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x0C) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xBB) #ll operand
    chip16.write_8bit(initial_address + 3, 0x10) #hh operand

    chip16.step()

    spu.play1500hz.assert_called_once_with(0x10BB)

def test_SNP():
    # Play tone from [RX] for HHLL ms.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x0D) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #x,y index operand
    chip16.write_8bit(initial_address + 2, 0xBB) #ll operand
    chip16.write_8bit(initial_address + 3, 0x10) #hh operand

    chip16.r[0x0] = 0xFAFA # register x(0) pointing to 0xFAFA
    chip16.write_16bit(0xFAFA, 0xBEEF) # value at 0xFAFA memory location is 0xAD

    chip16.step()

    spu.play_tone.assert_called_once_with(0xBEEF, 0x10BB)

def test_SNG():
    # Set sound generation parameters.
    spu = Mock()
    chip16 = cpu.Cpu()
    chip16.spu = spu

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x0E) #op code
    chip16.write_8bit(initial_address + 1, 0x33) #AD
    chip16.write_8bit(initial_address + 2, 0xBB) #sr operand
    chip16.write_8bit(initial_address + 3, 0x10) #vt operand

    chip16.step()

    spu.setup.assert_called_once_with(0x33, 0x10BB)

def test_JMP():
    # Set PC to HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x10) #op code
    chip16.write_8bit(initial_address + 1, 0x33) #AD
    chip16.write_8bit(initial_address + 2, 0xBB) #sr operand
    chip16.write_8bit(initial_address + 3, 0x10) #vt operand

    chip16.step()

    chip16.pc.should.be.eql(0x10BB)

def test_JMPx():
    #f x, then perform a JMP.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x12) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #y,x
    chip16.write_8bit(initial_address + 2, 0xBB) #hh
    chip16.write_8bit(initial_address + 3, 0x10) #ll

    chip16.write_8bit(initial_address + 4, 0x12) #op code
    chip16.write_8bit(initial_address + 5, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 6, 0xBB) #hh
    chip16.write_8bit(initial_address + 7, 0x10) #ll

    chip16.step()

    chip16.pc.should.be.eql(initial_address + 4)

    chip16.step()

    chip16.pc.should.be.eql(0x10BB)

def test_JME():
    #Set PC to HHLL if RX == RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x13) #op code
    chip16.write_8bit(initial_address + 1, 0b00010010) #y,x
    chip16.write_8bit(initial_address + 2, 0xBB) #hh
    chip16.write_8bit(initial_address + 3, 0x10) #ll

    chip16.r[1] = chip16.r[2] = 0xF

    chip16.step()

    chip16.pc.should.be.eql(0x10BB)

def test_CALL():
    # Store PC to [SP], increase SP by 2, set PC to HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x14) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #y,x
    chip16.write_8bit(initial_address + 2, 0xBB) #hh
    chip16.write_8bit(initial_address + 3, 0x10) #ll

    chip16.step()

    chip16.sp.should.be.eql(chip16.STACK_START + 2)
    chip16.read_8bit(chip16.sp - 2).should.be.eql(initial_address + 4)
    chip16.pc.should.be.eql(0x10BB)

def test_RET():
    # Decrease SP by 2, set PC to [SP].
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x14) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #y,x
    chip16.write_8bit(initial_address + 2, 0xBB) #hh
    chip16.write_8bit(initial_address + 3, 0x10) #ll

    chip16.write_8bit(0x10BB + 0, 0x15)
    chip16.write_8bit(0x10BB + 1, 0x0)
    chip16.write_8bit(0x10BB + 2, 0x0)
    chip16.write_8bit(0x10BB + 3, 0x0)

    chip16.step()

    chip16.sp.should.be.eql(chip16.STACK_START + 2)
    chip16.read_8bit(chip16.sp - 2).should.be.eql(initial_address + 4)
    chip16.pc.should.be.eql(0x10BB)

    chip16.step()

    chip16.pc.should.be.eql(initial_address + 4)

def test_JMP_RX():
    #Set PC to RX.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x16) #op code
    chip16.write_8bit(initial_address + 1, 0x00) #y,x
    chip16.write_8bit(initial_address + 2, 0x00) #hh
    chip16.write_8bit(initial_address + 3, 0x00) #ll

    chip16.r[0x0] = 0xFACA

    chip16.step()

    chip16.pc.should.be.eql(0xFACA)

def test_CALL_x():
    #If x, then perform a CALL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x17) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0xFA) #ll
    chip16.write_8bit(initial_address + 3, 0xCA) #hh

    chip16.step()

    chip16.pc.should.be.eql(0xCAFA)

def test_CALL_rx():
    #Store PC to [SP], increase SP by 2, set PC to RX.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x18) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0xFA) #ll
    chip16.write_8bit(initial_address + 3, 0xCA) #hh

    chip16.r[0x1] = 0xFACA

    chip16.step()

    chip16.pc.should.be.eql(0xFACA)
    chip16.sp.should.be.eql(chip16.STACK_START + 2)
    chip16.read_8bit(chip16.sp - 2).should.be.eql(initial_address + 4)

def test_ADDI_rx():
    #Set RX to RX+HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x40) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0x03) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x3

    chip16.step()

    chip16.r[0x1].should.be.eql(0x6)

def test_ADD_rx():
    #Set RX to RX+RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x41) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x03) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x3
    chip16.r[0x2] = 0x5

    chip16.step()

    chip16.r[0x1].should.be.eql(0x8)

def test_ADD_rz():
    #Set RZ to RX+RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x42) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x2
    chip16.r[0x2] = 0x5

    chip16.step()

    chip16.r[0x3].should.be.eql(0x7)

def test_SUB_rx():
    #Set RX to RX-HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x50) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x1) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x2

    chip16.step()

    chip16.r[0x1].should.be.eql(0x1)

def test_SUB_rx_ry():
    #Set RX to RX-RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x51) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x1) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x2
    chip16.r[0x2] = 0x2

    chip16.step()

    chip16.r[0x1].should.be.eql(0x0)

def test_SUB_rz():
    #Set RZ to RX-RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x52) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x6
    chip16.r[0x2] = 0x2

    chip16.step()

    chip16.r[0x3].should.be.eql(0x4)

def test_CMPI_hhll():
    #Compute RX-HHLL, discard result.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x53) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x11) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x11

    chip16.step()

    chip16.flag_zero.should.be.eql(0x1)

def test_CMPI_rx_ry():
    #Compute RX-RY, discard result.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x54) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x11) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0x1] = 0x11
    chip16.r[0x2] = 0x12

    chip16.step()

    chip16.flag_zero.should.be.eql(0x0)
    chip16.flag_negative.should.be.eql(0x1)

def test_ANDi():
    #Set RX to RX&HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x60) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000010) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00000010)

def test_AND_rx():
    #Set RX to RX&RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x61) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000010) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00000101

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00000101)

def test_AND_rz():
    #Set RZ to RX&RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x62) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00000101

    chip16.step()

    chip16.r[0x3].should.be.eql(0b00000101)

def test_TSTI():
    #Compute RX&HHLL, discard result.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x63) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000000) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111

    chip16.step()

    chip16.flag_zero.should.be.eql(0x1)

def test_TSTT():
    #Compute RX&RY, discard result.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x64) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000010) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b1000011110000111
    chip16.r[0x2] = 0b1000010110000111

    chip16.step()

    chip16.flag_negative.should.be.eql(0x1)

def test_ORI():
    #Set RX to RX|HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x70) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00000111)

def test_OR_ry():
    #Set RX to RX|RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x71) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00100100

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00100111)

def test_OR_rz():
    #Set RZ to RX|RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x72) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00100100

    chip16.step()

    chip16.r[0x3].should.be.eql(0b00100111)

def test_XORI():
    #Set RX to RX^HHLL.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x80) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00000100)

def test_XOR_ry():
    #Set RX to RX^RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x81) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00100100

    chip16.step()

    chip16.r[0x1].should.be.eql(0b00100011)

def test_XOR_rz():
    #Set RZ to RX^RY.
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x82) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0b00000011) #ll
    chip16.write_8bit(initial_address + 3, 0b00000000) #hh

    chip16.r[0x1] = 0b00000111
    chip16.r[0x2] = 0b00100100

    chip16.step()

    chip16.r[0x3].should.be.eql(0b00100011)

def test_MULI():
    #Set RX to RX*HHLL
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x90) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4

    chip16.step()

    chip16.r[0x1].should.be.eql(16)

def test_MUL_rx():
    #Set RX to RX*RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x91) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4
    chip16.r[0x2] = 0x2

    chip16.step()

    chip16.r[0x1].should.be.eql(8)

def test_MUL_rz():
    #Set RZ to RX*RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0x92) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0xFFFF
    chip16.r[0x2] = 0x2

    chip16.step()

    chip16.r[0x4].should.be.eql((0xFFFF * 0x2) & 0xFFFF)
    chip16.flag_carry.should.be.eql(0x1)
    chip16.flag_negative.should.be.eql(0x0)

def test_DIVI_rx():
    #Set RX to RX\HHLL
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA0) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4

    chip16.step()

    chip16.r[0x1].should.be.eql(0x1)
    chip16.flag_carry.should.be.eql(0x0)
    chip16.flag_negative.should.be.eql(0x0)

def test_DIV_rx():
    #Set RX to RX\RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA1) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4
    chip16.r[0x2] = 0x3

    chip16.step()

    chip16.r[0x1].should.be.eql(0x1)
    chip16.flag_carry.should.be.eql(0x1)
    chip16.flag_negative.should.be.eql(0x0)

def test_DIV_rz():
    #Set RZ to RX\RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA2) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x4) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4
    chip16.r[0x2] = 0x3

    chip16.step()

    chip16.r[0x4].should.be.eql(0x1)
    chip16.flag_carry.should.be.eql(0x1)
    chip16.flag_negative.should.be.eql(0x0)

def test_MODI():
    #Set RX to RX MOD HHLL
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA3) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x3) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4

    chip16.step()

    chip16.r[0x1].should.be.eql(0x4 % 0x3)

def test_MOD_rx_ry():
    #Set RX to RX MOD RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA4) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x0) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4
    chip16.r[0x2] = 0x3

    chip16.step()

    chip16.r[0x1].should.be.eql(0x4 % 0x3)

def test_MOD_rz():
    #Set RZ to RX MOD RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xA5) #op code
    chip16.write_8bit(initial_address + 1, 0b00100001) #y,x
    chip16.write_8bit(initial_address + 2, 0x3) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0x4
    chip16.r[0x2] = 0x3

    chip16.step()

    chip16.r[0x3].should.be.eql(0x4 % 0x3)

def test_SHL_rx():
    #Set RX to RX << N
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xB0) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0x3) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0b1

    chip16.step()

    chip16.r[0x1].should.be.eql(0b1000)

def test_SHR_rx():
    #Set RX to RX >> N
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xB1) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0x3) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0b10000

    chip16.step()

    chip16.r[0x1].should.be.eql(0b10)

def test_PUSH_rx():
    #Set [SP] to RX, increase SP by 2
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xC0) #op code
    chip16.write_8bit(initial_address + 1, 0b00110001) #y,x
    chip16.write_8bit(initial_address + 2, 0x0) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh

    chip16.r[0x1] = 0xFFAA
    original_sp = chip16.sp

    chip16.step()

    chip16.sp.should.be.eql(original_sp + 2)
    chip16.read_16bit(original_sp).should.be.eql(0xFFAA)

def test_POP_rx():
    #Decrease SP by 2, set RX to [SP]
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    #PUSH
    chip16.write_8bit(initial_address + 0, 0xC0) #op code
    chip16.write_8bit(initial_address + 1, 0b00110001) #y,x
    chip16.write_8bit(initial_address + 2, 0x0) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh
    #POP
    chip16.write_8bit(initial_address + 4, 0xC1) #op code
    chip16.write_8bit(initial_address + 5, 0b00100011) #y,x
    chip16.write_8bit(initial_address + 6, 0x0) #ll
    chip16.write_8bit(initial_address + 7, 0x0) #hh

    chip16.r[0x1] = 0xFFAA
    original_sp = chip16.sp

    chip16.step()
    chip16.step()

    chip16.sp.should.be.eql(original_sp)
    chip16.r[0x3].should.be.eql(0xFFAA)

def test_PUSHALL_and_POPALL():
    #Store R0..RF at [SP], increase SP by 32
    #Decrease SP by 32, load R0..RF from [SP]
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address
    #PUSHALL
    chip16.write_8bit(initial_address + 0, 0xC2) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #y,x
    chip16.write_8bit(initial_address + 2, 0x0) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh
    #POPALL
    chip16.write_8bit(initial_address + 4, 0xC3) #op code
    chip16.write_8bit(initial_address + 5, 0x0) #y,x
    chip16.write_8bit(initial_address + 6, 0x0) #ll
    chip16.write_8bit(initial_address + 7, 0x0) #hh

    original_sp = chip16.sp

    #random values to each register
    for x in range(0x0, 0xF + 1):
        chip16.r[x] = random.randint(0x0000, 0xFFFF)

    chip16.step()

    original_r0 = chip16.r[0x0]
    original_r1 = chip16.r[0x1]
    original_rf = chip16.r[0xF]

    chip16.sp.should.be.eql(original_sp + 32)
    chip16.read_16bit(original_sp).should.be.eql(original_r0)
    chip16.read_16bit(original_sp + 2).should.be.eql(original_r1)
    chip16.read_16bit(original_sp + 30).should.be.eql(original_rf)

    #another turn of random values to each register
    for x in range(0x0, 0xF + 1):
        chip16.r[x] = random.randint(0x0000, 0xFFFF)

    chip16.step()

    chip16.sp.should.be.eql(original_sp)
    chip16.r[0x0].should.be.eql(original_r0)
    chip16.r[0x1].should.be.eql(original_r1)
    chip16.r[0xF].should.be.eql(original_rf)

def test_PUSHF_and_POPF():
    #[0,Carry,Zero,0,0,0,Overflow,Negative]
    #Set [SP] to FLAGS, increase SP by 2
    #Decrease SP by 2, set FLAGS to [SP]
    carry_negative = 0b10000010
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    #PUSHF
    chip16.write_8bit(initial_address + 0, 0xC4) #op code
    chip16.write_8bit(initial_address + 1, 0x0) #y,x
    chip16.write_8bit(initial_address + 2, 0x0) #ll
    chip16.write_8bit(initial_address + 3, 0x0) #hh
    #POPF
    chip16.write_8bit(initial_address + 4, 0xC5) #op code
    chip16.write_8bit(initial_address + 5, 0x0) #y,x
    chip16.write_8bit(initial_address + 6, 0x0) #ll
    chip16.write_8bit(initial_address + 7, 0x0) #hh

    #SIMULATING A PUSH
    chip16.write_16bit(chip16.sp, carry_negative)

    chip16.step()

    chip16.flag_carry.should.be.eql(1)
    chip16.flag_negative.should.be.eql(1)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_overflow.should.be.eql(0)

    #FORCING A NEW FLAG
    chip16.flag_overflow = 1
    carry_negative_overflow = 0b11000010

    chip16.step()

    chip16.read_16bit(chip16.sp).should.be.eql(carry_negative_overflow)

def test_PAL_HHLL():
    #Load palette from [HHLL]
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xD0) #op code
    chip16.write_8bit(initial_address + 1, 0b00000000) #y,x
    chip16.write_8bit(initial_address + 2, 0xF0) #ll
    chip16.write_8bit(initial_address + 3, 0xBA) #hh

    palette_address = 0xBAF0
    chip16.write_8bit(palette_address + 0, 25)
    chip16.write_8bit(palette_address + 1, 50)
    chip16.write_8bit(palette_address + 2, 100)

    chip16.write_8bit(palette_address + 45, 125)
    chip16.write_8bit(palette_address + 46, 150)
    chip16.write_8bit(palette_address + 47, 200)

    for i in range(3, 45):
        chip16.write_8bit(palette_address + i, 225)

    chip16.step()

    chip16.gpu.palette[0]['r'].should.be.eql(float(25)/255)
    chip16.gpu.palette[0]['g'].should.be.eql(float(50)/255)
    chip16.gpu.palette[0]['b'].should.be.eql(float(100)/255)

    chip16.gpu.palette[10]['r'].should.be.eql(float(225)/255)
    chip16.gpu.palette[11]['g'].should.be.eql(float(225)/255)
    chip16.gpu.palette[12]['b'].should.be.eql(float(225)/255)

    chip16.gpu.palette[0xF]['r'].should.be.eql(float(125)/255)
    chip16.gpu.palette[0xF]['g'].should.be.eql(float(150)/255)
    chip16.gpu.palette[0xF]['b'].should.be.eql(float(200)/255)

def test_PAL_RX():
    #Load palette from [RX]
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address, 0xD1) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0xCA) #ll
    chip16.write_8bit(initial_address + 3, 0xFA) #hh

    palette_address = 0xBAF0
    chip16.r[3] = palette_address

    chip16.write_8bit(palette_address + 0, 25)
    chip16.write_8bit(palette_address + 1, 50)
    chip16.write_8bit(palette_address + 2, 100)

    chip16.write_8bit(palette_address + 45, 125)
    chip16.write_8bit(palette_address + 46, 150)
    chip16.write_8bit(palette_address + 47, 200)

    for i in range(3, 45):
        chip16.write_8bit(palette_address + i, 225)

    chip16.step()

    chip16.gpu.palette[0]['r'].should.be.eql(float(25)/255)
    chip16.gpu.palette[0]['g'].should.be.eql(float(50)/255)
    chip16.gpu.palette[0]['b'].should.be.eql(float(100)/255)

    chip16.gpu.palette[10]['r'].should.be.eql(float(225)/255)
    chip16.gpu.palette[11]['g'].should.be.eql(float(225)/255)
    chip16.gpu.palette[12]['b'].should.be.eql(float(225)/255)

    chip16.gpu.palette[0xF]['r'].should.be.eql(float(125)/255)
    chip16.gpu.palette[0xF]['g'].should.be.eql(float(150)/255)
    chip16.gpu.palette[0xF]['b'].should.be.eql(float(200)/255)

def test_NOTI_rx():
    #Set RX to NOT HHLL
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE0) #op code
    chip16.write_8bit(initial_address + 1, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 2, 0b11001100) #ll
    chip16.write_8bit(initial_address + 3, 0b00110011) #hh
    chip16.write_8bit(initial_address + 4, 0xE0) #op code
    chip16.write_8bit(initial_address + 5, 0b00000001) #y,x
    chip16.write_8bit(initial_address + 6, 0b11111111) #ll
    chip16.write_8bit(initial_address + 7, 0b11111111) #hh

    chip16.r[0x1] = 0xFACA

    chip16.step()

    chip16.r[0x1].should.be.eql(0b1100110000110011)
    chip16.r[0x1].should_not.be.eql(0xFACA)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(1)

    chip16.step()

    chip16.r[0x1].should.be.eql(0b0)
    chip16.flag_zero.should.be.eql(1)
    chip16.flag_negative.should.be.eql(0)

def test_NOT_rx():
    #Set RX to NOT RX
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE1) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0b0) #ll
    chip16.write_8bit(initial_address + 3, 0b0) #hh
    chip16.write_8bit(initial_address + 4, 0xE1) #op code
    chip16.write_8bit(initial_address + 5, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 6, 0b0) #ll
    chip16.write_8bit(initial_address + 7, 0b0) #hh

    chip16.r[0b11] = 0b0011001111001100

    chip16.step()

    chip16.r[0b11].should.be.eql(0b1100110000110011)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(1)

    chip16.r[0b11] = 0b1111111111111111

    chip16.step()

    chip16.r[0b11].should.be.eql(0b0)
    chip16.flag_zero.should.be.eql(1)
    chip16.flag_negative.should.be.eql(0)

def test_NOT_rx_ry():
    #Set RX to NOT RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE2) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0b0) #ll
    chip16.write_8bit(initial_address + 3, 0b0) #hh
    chip16.write_8bit(initial_address + 4, 0xE2) #op code
    chip16.write_8bit(initial_address + 5, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 6, 0b0) #ll
    chip16.write_8bit(initial_address + 7, 0b0) #hh

    chip16.r[0b0] = 0b0011001111001100

    chip16.step()

    chip16.r[0b11].should.be.eql(0b1100110000110011)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(1)

    chip16.r[0b0] = 0b1111111111111111

    chip16.step()

    chip16.r[0b11].should.be.eql(0b0)
    chip16.flag_zero.should.be.eql(1)
    chip16.flag_negative.should.be.eql(0)

def test_NEG_rx_hhll():
    #Set RX to NEG HHLL
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE3) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0x02) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.step()

    chip16.r[0b11].should.be.eql(-2)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(1)

def test_NEG_rx():
    #Set RX to NEG RX
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE4) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0x00) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0b11] = -2

    chip16.step()

    chip16.r[0b11].should.be.eql(2)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(0)

def test_NEG_rx_ry():
    #Set RX to NEG RY
    chip16 = cpu.Cpu()

    initial_address = 0x0000
    chip16.pc = initial_address

    chip16.write_8bit(initial_address + 0, 0xE5) #op code
    chip16.write_8bit(initial_address + 1, 0b00000011) #y,x
    chip16.write_8bit(initial_address + 2, 0x00) #ll
    chip16.write_8bit(initial_address + 3, 0x00) #hh

    chip16.r[0b0] = -2

    chip16.step()

    chip16.r[0b11].should.be.eql(2)
    chip16.flag_zero.should.be.eql(0)
    chip16.flag_negative.should.be.eql(0)

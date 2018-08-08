import wx
import sys, os
sys.path.append(os.path.abspath("../wxFormBuilder"))
import tinypycom_win
import serial
import threading

s_serialPort = serial.Serial()
s_recvInterval = 0.5

s_recvStatusFieldIndex = 0
s_sendStatusFieldIndex = 1
s_infoStatusFieldIndex = 2

s_recvStatusStr = 'Recv: '
s_recvTotalBytes = 0
s_sendStatusStr = 'Send: '
s_sendTotalBytes = 0


class mainWin(tinypycom_win.com_win):

    def setPort ( self ):
        s_serialPort.port = self.m_textCtrl_comPort.GetLineText(0)

    def setBaudrate ( self ):
        index = self.m_choice_baudrate.GetSelection()
        s_serialPort.baudrate = int(self.m_choice_baudrate.GetString(index))

    def setDatabits ( self ):
        index = self.m_choice_dataBits.GetSelection()
        m_dataBits = int(self.m_choice_dataBits.GetString(index))
        if m_dataBits == 5:
            s_serialPort.bytesizes = serial.FIVEBITS
        elif m_dataBits == 6:
            s_serialPort.bytesizes = serial.SIXBITS
        elif m_dataBits == 7:
            s_serialPort.bytesizes = serial.SEVENBITS
        elif m_dataBits == 8:
            s_serialPort.bytesizes = serial.EIGHTBITS
        else:
            pass

    def setStopbits ( self ):
        index = self.m_choice_stopBits.GetSelection()
        m_stopBits = self.m_choice_stopBits.GetString(index)
        if m_stopBits == '1':
            s_serialPort.stopbits = serial.STOPBITS_ONE
        elif m_stopBits == '1.5':
            s_serialPort.stopbits = serial.STOPBITS_ONE_POINT_FIVE
        elif m_stopBits == '2':
            s_serialPort.stopbits = serial.STOPBITS_TWO
        else:
            pass

    def setParitybits ( self ):
        index = self.m_choice_parityBits.GetSelection()
        m_parityBits = self.m_choice_parityBits.GetString(index)
        if m_parityBits == 'None':
            s_serialPort.parity = serial.PARITY_NONE
        elif m_parityBits == 'Odd':
            s_serialPort.parity = serial.PARITY_ODD
        elif m_parityBits == 'Even':
            s_serialPort.parity = serial.PARITY_EVEN
        elif m_parityBits == 'Mark':
            s_serialPort.parity = serial.PARITY_MARK
        elif m_parityBits == 'Space':
            s_serialPort.parity = serial.PARITY_SPACE
        else:
            pass

    def openClosePort( self, event ):
        if s_serialPort.isOpen():
            s_serialPort.close()
            self.m_button_openClose.SetLabel('Open')
            self.m_bitmap_led.SetBitmap(wx.Bitmap( u"../img/led_black.png", wx.BITMAP_TYPE_ANY ))
            self.statusBar_sizer.SetStatusText(s_serialPort.name + ' is closed', s_infoStatusFieldIndex)
        else:
            self.setPort()
            self.setBaudrate()
            self.setDatabits()
            self.setStopbits()
            self.setParitybits()
            s_serialPort.open()
            self.m_button_openClose.SetLabel('Close')
            self.m_bitmap_led.SetBitmap(wx.Bitmap( u"../img/led_green.png", wx.BITMAP_TYPE_ANY ))
            self.statusBar_sizer.SetFieldsCount(3)
            self.statusBar_sizer.SetStatusWidths([150, 150, 400])
            self.statusBar_sizer.SetStatusText(s_recvStatusStr + str(s_recvTotalBytes), s_recvStatusFieldIndex)
            self.statusBar_sizer.SetStatusText(s_sendStatusStr + str(s_sendTotalBytes), s_sendStatusFieldIndex)
            self.statusBar_sizer.SetStatusText(s_serialPort.name + ' is open, ' +
                                               str(s_serialPort.baudrate) + ', ' +
                                               str(s_serialPort.bytesizes) + ', ' +
                                               s_serialPort.parity + ', ' +
                                               str(s_serialPort.stopbits), s_infoStatusFieldIndex)
            s_serialPort.reset_input_buffer()
            s_serialPort.reset_output_buffer()
            threading.Timer(s_recvInterval, self.recvData).start()

    def clearSendDisplay( self, event ):
        self.m_textCtrl_send.Clear()

    def setSendFormat( self, event ):
        event.Skip()

    def sendData( self, event ):
        if s_serialPort.isOpen():
            lines = self.m_textCtrl_send.GetNumberOfLines()
            for i in range(0, lines):
                data = self.m_textCtrl_send.GetLineText(i)
                s_serialPort.write(str(data))
                global s_sendTotalBytes
                s_sendTotalBytes += len(data)
                self.statusBar_sizer.SetStatusText(s_sendStatusStr + str(s_sendTotalBytes), s_sendStatusFieldIndex)
        else:
            self.m_textCtrl_send.Clear()
            self.m_textCtrl_send.write('Port is not open')

    def clearRecvDisplay( self, event ):
        self.m_textCtrl_recv.Clear()

    def setRecvFormat( self, event ):
        event.Skip()

    def recvData( self ):
        if s_serialPort.isOpen():
            num = s_serialPort.inWaiting()
            if num != 0:
                data = s_serialPort.read(num)
                self.m_textCtrl_recv.write(data)
                global s_recvTotalBytes
                s_recvTotalBytes += len(data)
                self.statusBar_sizer.SetStatusText(s_recvStatusStr + str(s_recvTotalBytes), s_recvStatusFieldIndex)
            threading.Timer(s_recvInterval, self.recvData).start()

if __name__ == '__main__':
    app = wx.App()

    main_win = mainWin(None)
    main_win.SetTitle(u"tinyPyCOM v0.3.0 -- https://www.cnblogs.com/henjay724/")
    main_win.Show()

    app.MainLoop()

object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'Form1'
  ClientHeight = 300
  ClientWidth = 635
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Label1: TLabel
    Left = 136
    Top = 13
    Width = 97
    Height = 13
    Caption = 'Process is elevated?'
  end
  object Button1: TButton
    Left = 8
    Top = 8
    Width = 97
    Height = 25
    Caption = 'Install Profile'
    TabOrder = 0
    OnClick = Button1Click
  end
  object Button2: TButton
    Left = 8
    Top = 39
    Width = 97
    Height = 25
    Caption = 'Uninstall Profile'
    TabOrder = 1
    OnClick = Button2Click
  end
end

//
//  ViewController.swift
//  KMSample1
//
//  Created by Gabriel Wong on 2017-10-06.
//  Copyright © 2017 SIL International. All rights reserved.
//
import KeymanEngine
import UIKit

class ViewController: UIViewController, TextViewDelegate {
  @IBOutlet var textView: TextView!

  override func viewDidLoad() {
    super.viewDidLoad()

    Manager.shared.openURL = UIApplication.shared.openURL
    Manager.shared.isDebugPrintingOn = true
    Manager.shared.isKeymanHelpOn = false
    Manager.shared.preloadLanguageFile(atPath: Bundle.main.path(forResource: "tamil99m-1.1", ofType: "js")!,
                                       shouldOverwrite: true)
    Manager.shared.preloadFontFile(atPath: Bundle.main.path(forResource: "aava1", ofType: "ttf")!,
                                   shouldOverwrite: true)
    FontManager.shared.registerCustomFonts()

    Manager.shared.addKeyboard(Defaults.keyboard)
    let kb = InstallableKeyboard(id: "tamil99m",
                                 name: "Tamil 99M",
                                 languageID: "tam",
                                 languageName: "Tamil",
                                 version: "1.1",
                                 isRTL: false,
                                 font: Font(filename: "aava1.ttf"),
                                 oskFont: nil,
                                 isCustom: true)
    Manager.shared.addKeyboard(kb)

    textView.setKeymanDelegate(self)
    textView.viewController = self
  }
}

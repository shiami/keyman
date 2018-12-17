// Includes KeymanWeb's Device class, as it's quite a useful resource for KMW-related projects.
/// <reference path="../source/kmwdevice.ts" />
// Needed for OSK rendering to image files.
/// <reference path="../node_modules/html2canvas/dist/html2canvas.js" />
// Ensure that Promises are within scope.
/// <reference path="../node_modules/promise-polyfill/lib/polyfill.js" />

type KeyboardMap = {[id: string]: any};

namespace com.keyman.renderer {
  export class BatchRenderer {
    // Filters the keyboard array to ensure only a single entry remains, rather than an entry per language.
    private filterKeyboards(): KeyboardMap {
      let keyman = window['keyman'];

      let kbds = keyman['getKeyboards']();

      let keyboardMap = [];

      for(var i = 0; i < kbds.length; i++) {
        let id: string = kbds[i]['InternalName'];
        if(keyboardMap[id]) {
          continue;
        } else {
          keyboardMap[id] = kbds[i];
        }
      }

      return keyboardMap;
    }

    private render(resolve, ele: HTMLElement, layerIndex: number, isMobile?: boolean) {
      let html2canvas = window['html2canvas'];

      let imgOut = document.createElement('img');
      let br = document.createElement('br');
      document.body.appendChild(imgOut);
      document.body.appendChild(br);

      // Warning - needs Promises, so it'll need a polyfill for IE.
      let canvasParams = {
        'logging': false,
        'scale': 1,
        'width': window.innerWidth // Good for mobile, less-so for desktop.
      }

      if(!isMobile) {
        canvasParams['width'] = 500;
        ele.style.width = '500px';
      }

      html2canvas(ele, canvasParams).then(function(canvas) {
        imgOut.src = canvas.toDataURL();
        resolve(layerIndex);
      });
    }

    private processKeyboard(kbd) {
      let keyman = window['keyman'];
      let p: Promise<void> = keyman.setActiveKeyboard(kbd['InternalName']);
      let isMobile = keyman.util.device.formFactor != 'desktop';

      // A nice, closure-friendly reference for use in our callbacks.
      let renderer = this;
      // Really could use promises to tie these two together...

      return p.then(function() {
        let box: HTMLDivElement = keyman.osk._Box;
  
        // Uses 'private' APIs that may be subject to change in the future.  Keep it updated!
        let layers = keyman.keyboardManager.activeKeyboard.KV.KLS;

        let renderLayer = function(i) {
          return new Promise(function(resolve) {
            // (Private API) Directly sets the keyboard layer within KMW, then uses .show to force-display it.
            keyman.osk.layerId = Object.keys(layers)[i];
            keyman.osk.show(true);

            renderer.render(resolve, box, i, isMobile);
          })
        };

        // The resulting Promise will only call it's `.then()` once all of this keyboard's renders have been completed.
        return renderer.arrayPromiseIteration(renderLayer, Object.keys(layers).length);
      }).catch(function() {
        console.log("Failed to load the \"" + kbd['InternalName'] + "\" keyboard for rendering!");
        return Promise.resolve();
      });
    }

    // Synchronously performs asynchronous operations across a loop, one at a time.
    // Necessary due to the nature of KMW OSK rendering.
    private arrayPromiseIteration(promiseGenerator: (i: number) => Promise<any>, length: number): Promise<any> {
      let iteration = function(index: number): Promise<any> {
        if(index < length) {
          var promise = promiseGenerator(index);
          return promise.then(function(index: number) {
            return iteration(++index);
          })
        } else {
          return Promise.resolve();
        }
      }

      return iteration(0);
    }

    run() {
      if(window['keyman']) {
        let keyman = window['keyman'];

        // Establish a 'dummy' element to bypass the 'nothing's active' check KMW usualy uses.
        let dummy = document.createElement('imput');
        com.keyman['DOMEventHandlers'].states.activeElement = dummy;

        // We want the renderer to control where the keyboard is displayed.
        // Also bypasses another 'fun' OSK complication.
        keyman.osk.userPositioned = true;

        // Assumes that the keyboards have been preloaded for us.
        let kbds = this.filterKeyboards();

        console.log("Unique keyboard ids detected: " + Object.keys(kbds).length);

        let renderer = this;

        let keyboardIterator = function(i) {
          return new Promise(function(resolve) {
            renderer.processKeyboard(kbds[Object.keys(kbds)[i]]).then(function () {
              //console.log("Keyboard " + i + " processed!");
              resolve(i);
            });
          });
        };

        this.arrayPromiseIteration(keyboardIterator, Object.keys(kbds).length).then(function() {
          console.log("All keyboard renders are now complete!");
        });
      } else {
        console.error("KeymanWeb not detected!");
      }
    }
  }

  (function(){
    window['kmw_renderer'] = new com.keyman.renderer.BatchRenderer();
  })();
}
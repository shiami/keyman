/*
  Copyright:        Copyright (C) 2003-2018 SIL International.
  Authors:          mcdurdin
*/
#include "pch.h"   // I4128   // I4287


void KMX_Actions::ResetQueue()
{
  QueueSize = 0;   // I4262
}

KMX_Actions::KMX_Actions(KMX_Context *context)
{
  m_context = context;
  ResetQueue();
}

KMX_Actions::~KMX_Actions()
{
}

BOOL KMX_Actions::QueueAction(int ItemType, DWORD dwData)
{
  if (QueueSize > MAXACTIONQUEUE - 1)
  {
    DebugLog("App::QueueAction: queue size exceeded");
    return FALSE;
  }

  Queue[QueueSize].ItemType = ItemType;
  Queue[QueueSize].dwData = dwData;

  QueueSize++;

  int result = TRUE;
	
	switch(ItemType)
	{
	case QIT_VKEYDOWN:
		break;

	case QIT_DEADKEY:
		m_context->Add(UC_SENTINEL);
    m_context->Add(CODE_DEADKEY);
    m_context->Add((WORD) dwData);
		break;

	case QIT_CHAR:
    m_context->Add((WORD) dwData);
		break;

	case QIT_BACK:
		if(dwData == BK_BACKSPACE)  // User pressed backspace so delete deadkeys
			while(m_context->CharIsDeadkey()) m_context->Delete();

		//if(dwData == CODE_DEADKEY) break;
    m_context->Delete();

		if(dwData == BK_BACKSPACE)  // User pressed backspace so delete deadkeys
			while(m_context->CharIsDeadkey()) m_context->Delete();
		break;
	}

	return result;
}


BOOL KMX_Actions::CheckOutput(wchar_t *initialContext, wchar_t *expectedOutput) {
  //LogOutput();
  //console_log(L"--------------\n");

  wchar_t output[512] = L"", *p;

  wcscpy(output, initialContext);
  
  int i = 0, n = 0;

  p = wcschr(output, 0);

  for (; n < QueueSize; n++)
  {
    switch (Queue[n].ItemType) {
    case QIT_CAPSLOCK:
      //TODO: add Caps Event
      if (Queue[n].dwData == 0) {
        console_log(L"CAPSLOCK off\n");
      }
      else {
        console_log(L"CAPSLOCK on\n");
      }
      break;
    case QIT_VKEYDOWN:         
      if ((Queue[n].dwData & QVK_KEYMASK) == 0x05) Queue[n].dwData = (Queue[n].dwData & QVK_FLAGMASK) | VK_RETURN; // I649  // I3438

      /* 6.0.153.0: Fix repeat state for virtual keys */

      if ((Queue[n].dwData & QVK_KEYMASK) <= VK__MAX)  // I3438
      {
        console_log(L"KEYDOWN: %x (flags=%x)\n", Queue[n].dwData & 0xFF, (Queue[n].dwData & QVK_FLAGMASK) >> 16);
      }

      break;
    case QIT_VKEYUP:
      if ((Queue[n].dwData & QVK_KEYMASK) == 0x05) Queue[n].dwData = (Queue[n].dwData & QVK_FLAGMASK) | VK_RETURN; // I649  // I3438

      if ((Queue[n].dwData & QVK_KEYMASK) <= VK__MAX)  // I3438
      {
        console_log(L"KEYUP: %x (flags=%x)\n", Queue[n].dwData & 0xFF, (Queue[n].dwData & QVK_FLAGMASK) >> 16);
      }

      break;
    case QIT_VSHIFTDOWN:
      console_log(L"VSHIFTDOWN\n");
      break;
    case QIT_VSHIFTUP:
      console_log(L"VSHIFTUP\n");
      break;
    case QIT_CHAR:
      if (Uni_IsSMP(Queue[n].dwData)) {
        *p++ = (WCHAR) Uni_UTF32ToSurrogate1(Queue[n].dwData);
        *p++ = (WCHAR) Uni_UTF32ToSurrogate2(Queue[n].dwData);
      }
      else {
        *p++ = (WCHAR) Queue[n].dwData;
      }
      *p = 0;
      console_log(L"CHAR %x (%c)\n", Queue[n].dwData, Queue[n].dwData);
      break;
    case QIT_DEADKEY:
      console_log(L"DEADKEY\n");
      *p++ = UC_SENTINEL;
      *p++ = CODE_DEADKEY;
      *p++ = (WCHAR)(Queue[n].dwData + 1);
      *p = 0;
      break;
    case QIT_BELL:
      // TODO
      console_log(L"BELL\n");
      break;
    case QIT_BACK:
      console_log(L"BKSP (%x)\n", Queue[n].dwData);

      switch (Queue[n].dwData) {
      case BK_DEADKEY:
        assert(p > output);
        p = decxstr(p);
        assert(*p == UC_SENTINEL && *(p + 1) == CODE_DEADKEY);
        break;
      case BK_SUPP2:
        // TODO: eliminate BK_SUPP2
        break;
      case BK_BACKSPACE:
        // Delete deadkeys either side of our previous character
        // because this is a user-input backspace
        while (p > output) {
          p = decxstr(p);
          if (*p != UC_SENTINEL || *(p + 1) != CODE_DEADKEY) break;
        }
        if (p > output) {
          while (p > output) {
            p = decxstr(p);
            if (*p != UC_SENTINEL || *(p + 1) != CODE_DEADKEY) break;
          }
          p = incxstr(p);
        }
        *p = 0;
        break;
      default:
        assert(p > output);
        p = decxstr(p);
        *p = 0;
        break;
      }

      break;
    }
  }

  QueueSize = 0;

  BOOL result = !wcscmp(output, expectedOutput);

  wchar_t _context[256];
  m_context->Get(_context, 256);

  write_console(!result, L"context = %hs\n", Debug_UnicodeString(_context, 0));
  write_console(!result, L"output = %hs\n", Debug_UnicodeString(output, 0));
  write_console(!result, L"expected = %hs\n", Debug_UnicodeString(expectedOutput, 0));

  return result;
}


void KMX_Actions::LogOutput() {
  int i = 0, n = 0;

  for (; n < QueueSize; n++)
  {
    switch (Queue[n].ItemType) {
    case QIT_CAPSLOCK:
      //TODO: add Caps Event
      if (Queue[n].dwData == 0) {
        console_log(L"CAPSLOCK off\n");
      }
      else {
        console_log(L"CAPSLOCK on\n");
      }
      break;
    case QIT_VKEYDOWN:
      if ((Queue[n].dwData & QVK_KEYMASK) == 0x05) Queue[n].dwData = (Queue[n].dwData & QVK_FLAGMASK) | VK_RETURN; // I649  // I3438

      /* 6.0.153.0: Fix repeat state for virtual keys */

      if ((Queue[n].dwData & QVK_KEYMASK) <= VK__MAX)  // I3438
      {
        console_log(L"KEYDOWN: %x (flags=%x)\n", Queue[n].dwData & 0xFF, (Queue[n].dwData & QVK_FLAGMASK) >> 16);
      }

      break;
    case QIT_VKEYUP:
      if ((Queue[n].dwData & QVK_KEYMASK) == 0x05) Queue[n].dwData = (Queue[n].dwData & QVK_FLAGMASK) | VK_RETURN; // I649  // I3438

      if ((Queue[n].dwData & QVK_KEYMASK) <= VK__MAX)  // I3438
      {
        console_log(L"KEYUP: %x (flags=%x)\n", Queue[n].dwData & 0xFF, (Queue[n].dwData & QVK_FLAGMASK) >> 16);
      }

      break;
    case QIT_VSHIFTDOWN:
      console_log(L"VSHIFTDOWN\n");
      break;
    case QIT_VSHIFTUP:
      console_log(L"VSHIFTUP\n");
      break;
    case QIT_CHAR:
      console_log(L"CHAR %x (%c)\n", Queue[n].dwData, Queue[n].dwData);
      break;
    case QIT_DEADKEY:
      console_log(L"DEADKEY\n");
      break;
    case QIT_BELL:
      // TODO
      console_log(L"BELL\n");
      break;
    case QIT_BACK:
      console_log(L"BKSP (%x)\n", Queue[n].dwData);
      break;
    }
  }
}
import blpapi
import json

test_tickers = [
    'EUR1D25R BGN Curncy',
    'EURUSD1D25R BGN Curncy', 
    'EUR1DV BGN Curncy',
    'EURUSD1DV BGN Curncy',
    'EURUSDV1D BGN Curncy',
    'EURUSD1D Curncy',
    'EUR1D Curncy'
]

try:
    session = blpapi.Session()
    if not session.start():
        print('Failed to start session')
        exit()
    
    if not session.openService('//blp/refdata'):
        print('Failed to open service')
        exit()
    
    refDataService = session.getService('//blp/refdata')
    request = refDataService.createRequest('ReferenceDataRequest')
    
    for ticker in test_tickers:
        request.append('securities', ticker)
    
    request.append('fields', 'PX_LAST')
    request.append('fields', 'SECURITY_NAME')
    request.append('fields', 'SECURITY_DES')
    
    print('Testing tickers...')
    session.sendRequest(request)
    
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            if msg.messageType() == 'ReferenceDataResponse':
                secDataArray = msg.getElement('securityData')
                for i in range(secDataArray.numValues()):
                    secData = secDataArray.getValueAsElement(i)
                    security = secData.getElementAsString('security')
                    if secData.hasElement('securityError'):
                        error = secData.getElement('securityError')
                        print(f'{security}: ERROR - {error.getElementAsString("message")}')
                    elif secData.hasElement('fieldData'):
                        fieldData = secData.getElement('fieldData')
                        data = {}
                        if fieldData.hasElement('PX_LAST'):
                            data['PX_LAST'] = fieldData.getElementAsFloat('PX_LAST')
                        if fieldData.hasElement('SECURITY_NAME'):
                            data['SECURITY_NAME'] = fieldData.getElementAsString('SECURITY_NAME')
                        if fieldData.hasElement('SECURITY_DES'):
                            data['SECURITY_DES'] = fieldData.getElementAsString('SECURITY_DES')
                        print(f'{security}: {json.dumps(data)}')
                    else:
                        print(f'{security}: NO DATA')
        
        if ev.eventType() == blpapi.Event.RESPONSE:
            break
            
except Exception as e:
    print(f'Error: {str(e)}')
finally:
    if 'session' in locals():
        session.stop()
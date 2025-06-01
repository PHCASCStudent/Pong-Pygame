import React, { useEffect, useState } from 'react';
import { WebView } from 'react-native-webview';
import * as FileSystem from 'expo-file-system';
import { Asset } from 'expo-asset';
import * as ScreenOrientation from 'expo-screen-orientation';

const App = () => {
  const [html, setHtml] = useState(null);

  useEffect(() => {
    // Lock orientation to landscape
    ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE);

    (async () => {
      const asset = Asset.fromModule(require('./assets/index.html'));
      await asset.downloadAsync();
      const htmlString = await FileSystem.readAsStringAsync(asset.localUri);
      setHtml(htmlString);
    })();
  }, []);

  if (!html) return null;

  return (
    <WebView
      originWhitelist={['*']}
      source={{ html }}
      style={{ flex: 1 }}
    />
  );
};

export default App;
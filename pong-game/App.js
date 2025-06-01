import React, { useEffect, useState } from "react";
import { WebView } from "react-native-webview";
import * as FileSystem from "expo-file-system";
import { Asset } from "expo-asset";
import * as ScreenOrientation from "expo-screen-orientation";
import { AdMobBanner } from "expo-ads-admob";
import { Platform } from "react-native";

const App = () => {
  const [html, setHtml] = useState(null);
  const BANNER_AD_UNIT_ID = Platform.select({
    android: "ca-app-pub-5295742012044906/9653265755",
  });
  useEffect(() => {
    ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE);

    (async () => {
      const asset = Asset.fromModule(require("./assets/index.html"));
      await asset.downloadAsync();
      const htmlString = await FileSystem.readAsStringAsync(asset.localUri);
      setHtml(htmlString);
    })();
  }, []);

  if (!html) return null;

  return (
    <>
      <WebView originWhitelist={["*"]} source={{ html }} style={{ flex: 1 }} />
      <AdMobBanner
        bannerSize="smartBannerPortrait"
        adUnitID={BANNER_AD_UNIT_ID}
        servePersonalizedAds // true or false
        onDidFailToReceiveAdWithError={(error) => console.log(error)}
      />
    </>
  );
};

export default App;

chrome.contextMenus.create({
  id: "openInVLC",
  title: "Open in VLC",
  contexts: ["link", "video", "audio"]
  });

chrome.contextMenus.onClicked.addListener((info, tab) => {
if (info.menuItemId === "openInVLC") {
    chrome.runtime.sendNativeMessage("com.vlc.opener", {
    url: info.linkUrl || info.srcUrl
    }, (response) => {
    console.log("Response:", response);
    });
  }
});
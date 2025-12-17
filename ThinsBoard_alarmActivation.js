var downlinkPayload ={
    "alarm":01
};

var metadata = {
    "fPort": 15,
    "priority": "HIGH",
};
return {msg: downlinkPayload, metadata: metadata, msgType: "DOWNLINK_REQUEST"};

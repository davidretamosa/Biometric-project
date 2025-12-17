var data = decodeToJson(payload);
var deviceName = metadata.devideId;
var deviceType = metadata.applicationId;

var result={
    deviceName: deviceName,
    deviceType:deviceType,
    
    telemetry:{
        FC_max:data.FC_max,
        FC_media:data.FC_media,
        FC_min:data.FC_min
    },
    
    attributes:{
        fPort:metadata.fPort,
        devAddr:metadata.devAddr,
        eui: metadata.eui,
        metadata:metadata
    }
};


function decodeToString(payload){
    return String.fromCharCode.apply(String, payload);
}

function decodeToJson(payload){
    var str = decodeToString(payload);
    var data = JSON.parse(str);
    return data;
}

return result;
var data ={};
var confirmed=false;
var priority = "LOW";
var f_port=1;

if(metadata.confirmed != null)
    confirmed=metadata.confirmed

if(metadata.f_port!=null)
    f_port=metadata.f_port

if(metadata.priority!=null)
    priority=metadata.priority
    
var result = {
    contentType:"JSON",
    data: JSON.stringify({
        downlinks:[{
            f_port: f_port,
            confirmed:confirmed,
            frm_payload: "AQ==",
            priority: priority
        }]
    }),
    metadata:{
        devID:metadata.deviceName
    }
};
return result;
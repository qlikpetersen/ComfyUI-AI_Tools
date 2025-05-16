import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.KiersTests",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass.startsWith("CreateList")) {
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (side,slot,connect,link_info,output) {
                const r = onConnectionsChange?.apply(this, arguments);
                console.log("Someone changed my connection!");
                console.log([side,slot,connect,link_info,output]);
                if (side == 1) {
                    const [propName, propIndex] = output.name.split("-");
                    if (!isNaN(propIndex)) {
                        if (this.inputs.every((item) => item.link != undefined)) {
                            this.addInput(`${propName}-${parseInt(propIndex)+1}`, output.type);
                        }
                        if (!connect && this.inputs.length > 0) {
                            const index = this.inputs.findIndex((item) => item.name === output.name);
                            this.removeInput(index);
                        }
                        this.inputs.forEach((item, index) => {
                           item.name = `${propName}-${index}`;
                        });
                    }
                }
                return r;
            }
        }
    }
});

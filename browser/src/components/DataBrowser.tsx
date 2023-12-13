import { Box, Switch } from "@mui/material";
import { TracingNode, gatherKindsAndTags } from "../model/TracingNode";
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";
import ToggleButton from '@mui/material/ToggleButton';

import { RootPanel, RootsVisibility } from "./RootPanel";
import { TracingNodeView } from "./TracingNodeView";


export type BrowserConfig = {
    themeWithBoxes: boolean
}

export enum OpenerMode {
    Toggle,
    Open,
    Close
}

export type Opener = (keys: string | string[], mode: OpenerMode) => void


export function DataBrowser(props: { addInfo: AddInfo }) {
    const [config, setConfig] = useState<BrowserConfig>({ themeWithBoxes: false });
    const [selectedNode, setSelectedNode] = useState<TracingNode | null>(null);
    const [roots, setRoots] = useState<TracingNode[]>([]);
    const [opened, setOpened] = useState<Set<string>>(new Set());
    const [kinds, setKinds] = useState<Set<string>>(new Set());
    const [showRoots, setShowRoots] = useState<RootsVisibility>({ showFinished: true, showFailed: true });


    function refresh() {
        callGuard(async () => {
            const response1 = await axios.get(SERVICE_PREFIX + "/nodes/list");
            if (response1 === null) {
                return;
            }
            const uids = response1.data as string[];

            const forget_open = roots.filter(c => c.state !== 'open');
            const local_uids = new Set(forget_open.map(c => c.uid));
            const to_download: string[] = [];
            for (const uid of uids) {
                if (!local_uids.has(uid)) {
                    to_download.push(uid);
                }
            }
            const response2 = await axios.post(SERVICE_PREFIX + "/nodes/roots", { "uids": to_download });
            if (response2 === null) {
                return;
            }
            const new_roots = response2.data as TracingNode[];
            const uids_set = new Set(uids);

            const final_roots = forget_open.filter((c) => uids_set.has(c.uid)).concat(new_roots);
            final_roots.sort()

            final_roots.sort((a, b) => {
                if (a.start_time && b.start_time) {
                    if (a.start_time < b.start_time) {
                        return 1;
                    }
                    if (a.start_time > b.start_time) {
                        return -1;
                    }
                }
                return 0;
            });

            setRoots(final_roots);

            if (selectedNode === null && final_roots.length > 0) {
                selectRoot(final_roots[0].uid);
            } else if (selectedNode !== null && final_roots.find((x) => x.uid === selectedNode.uid)) {
                selectRoot(selectedNode.uid);
            } else {
                setSelectedNode(null);
            }
        }, props.addInfo);
    }

    function selectRoot(root: string) {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/nodes/uid/" + root);
            const node = response.data as TracingNode;
            setSelectedNode(node);
            setOpened((op) => {
                const o = new Set(op);
                o.add(root);
                if (newKinds.size !== kinds.size) {
                    newKinds.forEach((k) => {
                        if (!kinds.has(k)) {
                            o.add(k);
                        }
                    })
                }
                return o;
            })
            const newKinds = new Set(kinds);
            gatherKindsAndTags(node, newKinds);
            if (newKinds.size !== kinds.size) {
                setKinds(newKinds);
            }
        }, props.addInfo)
    }

    function setOpen(keys: string | string[], mode: OpenerMode) {
        setOpened((op) => {
            const o = new Set(op);
            if (!Array.isArray(keys)) {
                keys = [keys]
            }
            if (mode === OpenerMode.Toggle) {
                for (const key of keys) {
                    if (!o.delete(key)) {
                        o.add(key)
                    }
                }
            } else if (mode === OpenerMode.Open) {
                for (const key of keys) {
                    o.add(key)
                }
            } else {
                for (const key of keys) {
                    o.delete(key)
                }
            }
            return o;
        })

    }

    const sortedKinds = Array.from(kinds);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { refresh() }, []);

    return <div>
        <RootPanel showRoots={showRoots} setShowRoots={setShowRoots} roots={roots} selectedNode={selectedNode} refresh={refresh} selectRoot={selectRoot} addInfo={props.addInfo} />
        <div style={{ float: "left", width: "calc(100% - 365px)", overflow: 'auto' }}>
            <Box
                m={1} //margin
                display="flex"
                justifyContent="flex-start"
                alignItems="flex-start"
            >
                <Switch
                    checked={config.themeWithBoxes}
                    onChange={(e) => setConfig({ ...config, themeWithBoxes: e.target.checked })}
                />
                {sortedKinds.map((kind) => <ToggleButton sx={{ paddingTop: 0.2, paddingBottom: 0.2, marginLeft: 0.5 }} value={""} selected={opened.has(kind)} onChange={() => setOpen(kind, OpenerMode.Toggle)} key={kind}>{kind}</ToggleButton>)}
            </Box>
            {selectedNode && <TracingNodeView node={selectedNode} opened={opened} setOpen={setOpen} config={config}></TracingNodeView>}
            {roots.length === 0 && !selectedNode && <span>No nodes registed in Data Browser</span>}
        </div>
    </div >
}
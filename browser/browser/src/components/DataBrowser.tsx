import { Grid, ListItemButton, ListItemText, Paper } from "@mui/material"
import { Context } from "../model/Context"
import { ContextNode } from "./ContextNode"
import { useEffect, useState } from "react";
import axios from "axios";
import { SERVICE_PREFIX } from "../config";
import { callGuard } from "../common/guard";
import { AddInfo } from "../common/info";

// type Root = {
//     name: string,
//     uuid: string,
// }


export function DataBrowser(props: { addInfo: AddInfo }) {
    const [roots, setRoots] = useState<string[]>([]);
    const [selectedCtx, setSelectedCtx] = useState<Context | null>(null);

    function refresh() {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/list");
            if (response === null) {
                return;
            }
            const rs = response.data as string[];
            setRoots(rs);
            if (rs.length > 0) {
                selectRoot(rs[0]);
            }
        }, props.addInfo);
    }

    function selectRoot(root: string) {
        callGuard(async () => {
            const response = await axios.get(SERVICE_PREFIX + "/contexts/uuid/" + root);
            const ctx = response.data as Context;
            setSelectedCtx(ctx);
        }, props.addInfo)
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(refresh, []);

    return <Grid container>
        <Grid item xs={2}>
            <Paper>
                {roots.map((root) =>
                    <ListItemButton key={root} component="a" onClick={() => selectRoot(root)}>
                        <ListItemText primary={root.slice(0, 8)} />
                    </ListItemButton>
                )}
            </Paper>
        </Grid>
        <Grid item xs={9}>
            {selectedCtx && <ContextNode context={selectedCtx} depth={0} />}
            {roots.length === 0 && !selectedCtx && <span>No context registed in Data Browser</span>}
        </Grid>
    </Grid>
}
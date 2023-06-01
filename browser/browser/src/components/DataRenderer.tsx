import { Button } from "@mui/material";
import { UUID } from "crypto";


export function DataRenderer(props: { data: any, uuid: string, opened: Set<string>, toggleOpen: (uuid: string) => void, hideType?: string }) {
    let d = props.data;
    if (typeof d === 'boolean') {
        return <span>{d ? "true" : "false"}</span>
    }
    if (typeof d === 'number' || typeof d === 'string') {
        return <span>{d}</span>
    }

    const children = [];
    let type = null;
    for (const property in d) {
        const value = d[property];
        if (property === "_type") {
            type = value;
            continue;
        }
        children.push({ property: property, value: value });
    }

    const isLong = children.length > 3;

    if (isLong && !props.opened.has(props.uuid)) {
        return <>
            {(props.hideType !== type && type) && <span>{type}</span>}
            <Button onClick={() => props.toggleOpen(props.uuid)}>Show {children.length} items</Button>
        </>
    }

    return (<>
        {(props.hideType !== type && type) && <span>{type}</span>}
        {isLong && <Button onClick={() => props.toggleOpen(props.uuid)}>Hide items</Button>}
        <ul>
            {children.map(({ property, value }) => <li key={property}><strong>{property}</strong>: <DataRenderer uuid={props.uuid + "/" + property} data={value} opened={props.opened} toggleOpen={props.toggleOpen} /></li>)}
        </ul></>);
}
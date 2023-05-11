

export function DataRenderer(props: { data: any, hideType?: string }) {
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

    return (<>{(props.hideType !== type && type) && <span>{type}</span>}<ul>
        {children.map(({ property, value }) => <li><strong>{property}</strong>: <DataRenderer data={value} /></li>)}
    </ul></>);
}
import Color from 'colorjs.io';
import seedrandom from 'seedrandom';

export function colorForString(str: string, saturation = 0.7, lightness = 0.5, varyLightnessRate = 0.2, varySaturationRate = 0.3): Color {
    const rng = seedrandom(str);
    return new Color("hsl", [
        rng() * 360,
        saturation * (varySaturationRate * (2 * rng() - 1)),
        lightness * (varyLightnessRate * (2 * rng() - 1))
    ]);
}

export function generateUid(name: string): string {
    const escapeNameRe = /[^a-zA-Z0-9]/g;
    const cleanedName = name.substring(0, 16).replace(escapeNameRe, "_");
    const randomPart = Array.from({ length: 6 }, () => (Math.random() * 35).toString(36)).join('');
    const uid = `${new Date().toISOString()}-${cleanedName}-${randomPart}`;
    return uid.replace(/[:/\\]/g, "-");
}

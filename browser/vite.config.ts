import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        rollupOptions: {
            output: {
                // Default format gives some warnings in Jupyter (because redefining items)
                // However when format: "iife" is used then CSS does not work
                // And it disables "fading out of long text"
            }
        }
    }
})

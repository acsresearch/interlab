import { BaseMemory } from './memory/BaseMemory';

export abstract class ActorWithMemory extends BaseActor {
    memory: BaseMemory; // BaseMemory type is assumed

    constructor(name?: string, memory?: BaseMemory, style?: { [key: string]: any }) {
        super(name, style);
        this.memory = memory || new DefaultMemory(); // Assuming DefaultMemory is a concrete implementation of BaseMemory
    }

    _observe(event: Event): void { // Event type is assumed
        this.memory.addEvent(event);
    }

    copy(): ActorWithMemory {
        const actor = Object.create(this);
        actor.memory = this.memory.copy();
        return actor;
    }
}

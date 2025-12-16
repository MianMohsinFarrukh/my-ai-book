import React from 'react';
import clsx from 'clsx';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './EmbodiedIntelligenceSection.module.css';

export default function EmbodiedIntelligenceSection() {
  return (
    <section className={clsx('container', styles.section)}>
      <div className="row">
        <div className="col col--12">
          <h2 id="embodied-intelligence">Embodied Intelligence Explained</h2>
          <p>
            Embodied Intelligence is the theory that intelligence emerges from the interaction between
            an agent's cognitive processes and its physical body within an environment. This approach
            suggests that true artificial intelligence cannot be achieved through purely symbolic
            computation, but must be grounded in physical interaction with the world.
          </p>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--6">
              <h3>Key Principles</h3>
              <ul>
                <li><strong>Embodiment</strong>: Intelligence is shaped by the physical form of the agent</li>
                <li><strong>Environment Interaction</strong>: Cognitive processes emerge from environmental engagement</li>
                <li><strong>Morphological Computation</strong>: The body contributes to computation and control</li>
                <li><strong>Emergent Behavior</strong>: Complex behaviors arise from simple interactions</li>
              </ul>
            </div>
            <div className="col col--6">
              <div className={styles.imageContainer}>
                <img
                  src={useBaseUrl('/img/home/embodied-intelligence.jpg')}
                  alt="Embodied intelligence visualization"
                  className={styles.sectionImage}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
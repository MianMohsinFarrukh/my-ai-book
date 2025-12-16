import React from 'react';
import clsx from 'clsx';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './PhysicalAISection.module.css';

export default function PhysicalAISection() {
  return (
    <section className={clsx('container', styles.section)}>
      <div className="row">
        <div className="col col--12">
          <h2 id="physical-ai">What is Physical AI?</h2>
          <p>
            Physical AI represents the convergence of artificial intelligence with the physical world.
            Unlike traditional AI that operates in digital spaces, Physical AI systems interact directly
            with the physical environment through sensors and actuators, creating intelligent agents that
            can perceive, reason, and act in real-world contexts.
          </p>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--4">
              <div className={styles.featureCard}>
                <h3>Perception</h3>
                <p>Real-world sensing through cameras, LiDAR, IMU, and other sensors to understand the environment.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.featureCard}>
                <h3>Reasoning</h3>
                <p>AI algorithms that process sensor data to make decisions in dynamic physical environments.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.featureCard}>
                <h3>Action</h3>
                <p>Physical execution of intelligent behaviors through robotic actuators and control systems.</p>
              </div>
            </div>
          </div>

          <div className={styles.imageContainer}>
            <img
              src={useBaseUrl('/img/home/physical-ai-concept.jpg')}
              alt="Physical AI concept visualization"
              className={styles.sectionImage}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
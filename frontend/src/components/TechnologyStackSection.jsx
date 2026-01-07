import React from 'react';
import clsx from 'clsx';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './TechnologyStackSection.module.css';

export default function TechnologyStackSection() {
  return (
    <section className={clsx('container', styles.section)}>
      <div className="row">
        <div className="col col--12">
          <h2 id="technology-stack">Technology Stack Overview</h2>
          <p>
            Our Physical AI & Humanoid Robotics curriculum is built on industry-standard technologies
            that power modern robotics and AI systems. These tools provide the foundation for
            developing embodied intelligence systems.
          </p>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>ROS 2</h3>
                <p>The Robot Operating System provides the communication framework and tools for building robotic applications.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>Gazebo</h3>
                <p>High-fidelity physics simulation environment for testing and validating robotic systems.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>NVIDIA Isaac</h3>
                <p>Simulation and AI framework for developing perception and control systems.</p>
              </div>
            </div>
          </div>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>Vision-Language-Action</h3>
                <p>Integrated systems that connect visual perception, language understanding, and physical action.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>Unity</h3>
                <p>Real-time development platform for creating immersive simulation environments.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.techCard}>
                <h3>Simulation-to-Reality</h3>
                <p>Techniques for transferring learned behaviors from simulation to real robots.</p>
              </div>
            </div>
          </div>

          <div className={styles.imageContainer}>
            <img
              src={useBaseUrl('/img/home/tech-stack.jpg')}
              alt="Technology stack visualization"
              className={styles.sectionImage}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './CapstoneProjectSection.module.css';

export default function CapstoneProjectSection() {
  return (
    <section className={clsx('container', styles.section)}>
      <div className="row">
        <div className="col col--12">
          <h2 id="capstone-project">Capstone Project: Humanoid Control System</h2>
          <p>
            The capstone project challenges students to integrate all concepts learned throughout the course
            by developing a complete humanoid robot control system that demonstrates embodied intelligence
            through voice command interpretation, path planning, and object manipulation.
          </p>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--4">
              <div className={styles.projectCard}>
                <h3>Voice Command Processing</h3>
                <p>Implement speech-to-text and natural language processing for robot command interpretation.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.projectCard}>
                <h3>Path Planning</h3>
                <p>Develop navigation algorithms for safe and efficient movement in dynamic environments.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.projectCard}>
                <h3>Object Manipulation</h3>
                <p>Create perception and control systems for grasping and manipulating objects.</p>
              </div>
            </div>
          </div>

          <div className={styles.buttonContainer}>
            <Link
              className="button button--primary button--lg"
              to="/docs/capstone-project">
              Explore Capstone Project
            </Link>
          </div>

          <div className={styles.imageContainer}>
            <img
              src={useBaseUrl('/img/home/capstone-project.jpg')}
              alt="Capstone project humanoid robot visualization"
              className={styles.sectionImage}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
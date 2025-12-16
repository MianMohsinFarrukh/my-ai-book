import React from 'react';
import clsx from 'clsx';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './LearningOutcomesSection.module.css';

export default function LearningOutcomesSection() {
  return (
    <section className={clsx('container', styles.section)}>
      <div className="row">
        <div className="col col--12">
          <h2 id="learning-outcomes">Learning Outcomes</h2>
          <p>
            Upon completing this course, students will be able to understand and implement key concepts
            in Physical AI and embodied intelligence. The curriculum is designed to provide both
            theoretical knowledge and practical skills.
          </p>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--6">
              <h3>Conceptual Understanding</h3>
              <ul>
                <li>Explain the principles of embodied intelligence and physical AI</li>
                <li>Describe the relationship between perception, cognition, and action</li>
                <li>Understand the role of simulation in robotics development</li>
                <li>Analyze the challenges of sim-to-real transfer</li>
              </ul>
            </div>
            <div className="col col--6">
              <h3>Practical Skills</h3>
              <ul>
                <li>Develop robotic applications using ROS 2</li>
                <li>Implement perception systems with computer vision</li>
                <li>Create control algorithms for robotic systems</li>
                <li>Deploy AI models on robotic platforms</li>
              </ul>
            </div>
          </div>

          <div className={styles.imageContainer}>
            <img
              src={useBaseUrl('/img/home/learning-outcomes.jpg')}
              alt="Learning outcomes visualization"
              className={styles.sectionImage}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
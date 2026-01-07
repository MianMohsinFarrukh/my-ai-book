import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './HeroSection.module.css';

export default function HeroSection() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className="row">
          <div className="col col--5">
            <h1 className="hero__title">{siteConfig.title}</h1>
            <p className="hero__subtitle">{siteConfig.tagline}</p>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/docs/course-outline">
                Start Learning - 5 min ⏱️
              </Link>
            </div>
          </div>
          <div className="col col--7">
            <div className={styles.heroImageContainer}>
              <img
                src={useBaseUrl('/img/home/futuristic.avif')}
                alt="Humanoid robot with AI brain visualization"
                className={styles.heroImage}
              />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
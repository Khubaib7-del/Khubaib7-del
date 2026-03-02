<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khubaib Nazeer - Full Stack Developer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #00d9ff;
            --secondary: #ff006e;
            --accent: #8338ec;
            --dark: #0a0e27;
            --light: #f8f9fa;
            --gray: #a0aec0;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1a1f3a 100%);
            color: var(--light);
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* Animated background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 217, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(131, 56, 236, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Header Section */
        header {
            text-align: center;
            margin-bottom: 60px;
            animation: fadeInDown 0.8s ease-out;
        }

        .name {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }

        .tagline {
            font-size: 1.3rem;
            color: var(--gray);
            margin-bottom: 30px;
            font-weight: 500;
        }

        .contact-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 20px;
        }

        .contact-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border: 2px solid var(--primary);
            border-radius: 50px;
            color: var(--primary);
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .contact-link:hover {
            background: var(--primary);
            color: var(--dark);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.3);
        }

        /* About Section */
        .about {
            margin-bottom: 80px;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }

        .section-title {
            font-size: 2rem;
            margin-bottom: 20px;
            display: inline-block;
            position: relative;
            padding-bottom: 10px;
        }

        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 2px;
        }

        .about-text {
            color: var(--gray);
            font-size: 1.1rem;
            line-height: 1.8;
            margin-top: 20px;
        }

        /* Skills Section */
        .skills-section {
            margin-bottom: 80px;
            animation: fadeInUp 0.8s ease-out 0.4s both;
        }

        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .skill-category {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }

        .skill-category:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--primary);
            box-shadow: 0 8px 32px rgba(0, 217, 255, 0.15);
            transform: translateY(-5px);
        }

        .skill-category-title {
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--primary);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            background: rgba(131, 56, 236, 0.2);
            border: 1px solid rgba(131, 56, 236, 0.5);
            border-radius: 20px;
            font-size: 0.85rem;
            color: var(--primary);
            transition: all 0.3s ease;
            cursor: pointer;
            font-weight: 500;
        }

        .badge:hover {
            background: var(--accent);
            border-color: var(--accent);
            color: var(--light);
            transform: scale(1.05);
        }

        /* What I Do Section */
        .what-i-do {
            margin-bottom: 80px;
            animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .feature-card {
            padding: 30px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(0, 217, 255, 0.15);
            border-radius: 12px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 217, 255, 0.1), transparent);
            transition: left 0.5s ease;
        }

        .feature-card:hover::before {
            left: 100%;
        }

        .feature-card:hover {
            border-color: var(--primary);
            background: rgba(0, 217, 255, 0.05);
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }

        .feature-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 10px;
            color: var(--primary);
        }

        .feature-desc {
            color: var(--gray);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Learning Section */
        .learning-section {
            margin-bottom: 80px;
            animation: fadeInUp 0.8s ease-out 0.8s both;
        }

        .learning-items {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .learning-item {
            padding: 15px;
            background: rgba(255, 0, 110, 0.1);
            border-left: 3px solid var(--secondary);
            border-radius: 5px;
            color: var(--light);
            transition: all 0.3s ease;
        }

        .learning-item:hover {
            background: rgba(255, 0, 110, 0.15);
            border-left-color: var(--primary);
            transform: translateX(5px);
        }

        /* Footer */
        footer {
            text-align: center;
            padding-top: 40px;
            border-top: 1px solid rgba(0, 217, 255, 0.2);
            margin-top: 60px;
            color: var(--gray);
            animation: fadeIn 0.8s ease-out 1s both;
        }

        .cta-button {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: var(--dark);
            text-decoration: none;
            border-radius: 50px;
            font-weight: 700;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            font-size: 1rem;
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0, 217, 255, 0.3);
        }

        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .name {
                font-size: 2.5rem;
            }

            .tagline {
                font-size: 1.1rem;
            }

            .section-title {
                font-size: 1.5rem;
            }

            .skills-grid {
                grid-template-columns: 1fr;
            }

            .features-grid {
                grid-template-columns: 1fr;
            }

            .contact-links {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1 class="name">Khubaib Nazeer</h1>
            <p class="tagline">Full-Stack Developer & Problem Solver</p>
            <p class="tagline" style="color: rgba(255, 255, 255, 0.6); font-size: 1rem;">Building efficient solutions with modern technologies</p>
            
            <div class="contact-links">
                <a href="mailto:khubaibnazeer8@gmail.com" class="contact-link">
                    ✉️ Email
                </a>
                <a href="https://www.linkedin.com/in/khubaib-nazeer/" class="contact-link">
                    💼 LinkedIn
                </a>
                <a href="https://github.com" class="contact-link">
                    🐙 GitHub
                </a>
            </div>
        </header>

        <!-- About -->
        <section class="about">
            <h2 class="section-title">About Me</h2>
            <p class="about-text">
                I'm a dedicated developer with expertise in building robust applications across the full stack. I love tackling algorithmic challenges, writing clean code, and continuously learning new technologies. With a strong foundation in both systems programming and web development, I'm passionate about creating efficient, scalable solutions.
            </p>
        </section>

        <!-- Skills -->
        <section class="skills-section">
            <h2 class="section-title">Technical Skills</h2>
            
            <div class="skills-grid">
                <!-- Languages -->
                <div class="skill-category">
                    <div class="skill-category-title">💻 Languages</div>
                    <div class="badge-container">
                        <span class="badge">C++</span>
                        <span class="badge">Python</span>
                        <span class="badge">JavaScript</span>
                        <span class="badge">Assembly</span>
                        <span class="badge">HTML5</span>
                        <span class="badge">CSS3</span>
                    </div>
                </div>

                <!-- Core Concepts -->
                <div class="skill-category">
                    <div class="skill-category-title">🎯 Core Concepts</div>
                    <div class="badge-container">
                        <span class="badge">OOP</span>
                        <span class="badge">DSA</span>
                        <span class="badge">Design Patterns</span>
                    </div>
                </div>

                <!-- Databases -->
                <div class="skill-category">
                    <div class="skill-category-title">🗄️ Databases</div>
                    <div class="badge-container">
                        <span class="badge">SQL</span>
                        <span class="badge">Query Optimization</span>
                    </div>
                </div>

                <!-- Data Science -->
                <div class="skill-category">
                    <div class="skill-category-title">📊 Data Science</div>
                    <div class="badge-container">
                        <span class="badge">NumPy</span>
                        <span class="badge">Pandas</span>
                        <span class="badge">Matplotlib</span>
                    </div>
                </div>

                <!-- Tools -->
                <div class="skill-category">
                    <div class="skill-category-title">🛠️ Tools</div>
                    <div class="badge-container">
                        <span class="badge">Git</span>
                        <span class="badge">GitHub</span>
                        <span class="badge">VS Code</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- What I Do -->
        <section class="what-i-do">
            <h2 class="section-title">What I Do</h2>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🚀</div>
                    <div class="feature-title">Full-Stack Development</div>
                    <div class="feature-desc">Building end-to-end applications with modern tech stacks and best practices.</div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <div class="feature-title">Data Analysis</div>
                    <div class="feature-desc">Processing and visualizing data with Python & scientific libraries.</div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Algorithm Optimization</div>
                    <div class="feature-desc">Designing efficient solutions for complex problems with optimal time & space complexity.</div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🎨</div>
                    <div class="feature-title">Web Development</div>
                    <div class="feature-desc">Creating responsive and interactive web experiences with modern frameworks.</div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🏗️</div>
                    <div class="feature-title">Software Architecture</div>
                    <div class="feature-desc">Implementing OOP principles, design patterns, and clean architecture.</div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🔧</div>
                    <div class="feature-title">System Programming</div>
                    <div class="feature-desc">Low-level optimizations and performance tuning in C++ and Assembly.</div>
                </div>
            </div>
        </section>

        <!-- Currently Learning -->
        <section class="learning-section">
            <h2 class="section-title">Currently Exploring</h2>
            
            <div class="learning-items">
                <div class="learning-item">🤖 Machine Learning & AI</div>
                <div class="learning-item">☁️ Cloud Computing</div>
                <div class="learning-item">🔒 Cybersecurity</div>
                <div class="learning-item">📱 Mobile Development</div>
                <div class="learning-item">🌐 Web3 & Blockchain</div>
                <div class="learning-item">🧪 Open Source Contribution</div>
            </div>
        </section>

        <!-- Footer -->
        <footer>
            <p>Let's build something amazing together! 🚀</p>
            <p style="margin-top: 15px; font-size: 0.9rem;">Interested in collaboration? Feel free to reach out!</p>
            <a href="mailto:khubaibnazeer8@gmail.com" class="cta-button">Get In Touch</a>
            <p style="margin-top: 30px; font-size: 0.85rem;">© 2024 Khubaib Nazeer. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>

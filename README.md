<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khubaib Nazeer - GitHub README</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #0ea5e9;
            --secondary: #f43f5e;
            --accent: #8b5cf6;
            --bg: #0f172a;
            --text: #f1f5f9;
            --gray: #94a3b8;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, var(--bg) 0%, #1e293b 100%);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 60px 20px;
        }

        /* Header */
        h1 {
            font-size: 2.5rem;
            margin-bottom: 8px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 1.2rem;
            color: var(--gray);
            margin-bottom: 30px;
        }

        .intro {
            color: var(--gray);
            margin-bottom: 30px;
            line-height: 1.8;
            font-size: 1.05rem;
        }

        /* Section Titles */
        h2 {
            font-size: 1.8rem;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary);
            display: inline-block;
        }

        /* Links */
        a {
            color: var(--primary);
            text-decoration: none;
            transition: color 0.3s;
        }

        a:hover {
            color: var(--secondary);
            text-decoration: underline;
        }

        /* Badge Styles */
        .badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: rgba(14, 165, 233, 0.1);
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 20px;
            font-size: 0.9rem;
            color: var(--primary);
            font-weight: 500;
            transition: all 0.3s;
        }

        .badge:hover {
            background: rgba(14, 165, 233, 0.2);
            border-color: var(--primary);
            transform: translateY(-2px);
        }

        /* Skills Grid */
        .skills-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }

        .skill-box {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(14, 165, 233, 0.2);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }

        .skill-box:hover {
            border-color: var(--primary);
            background: rgba(14, 165, 233, 0.05);
            transform: translateY(-3px);
        }

        .skill-title {
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 12px;
            font-size: 1.1rem;
        }

        .skill-items {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .skill-tag {
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            color: var(--text);
        }

        /* Features Grid */
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }

        .feature-item {
            background: rgba(30, 41, 59, 0.4);
            border-left: 3px solid var(--primary);
            padding: 15px;
            border-radius: 4px;
            transition: all 0.3s;
        }

        .feature-item:hover {
            border-left-color: var(--secondary);
            background: rgba(30, 41, 59, 0.6);
        }

        .feature-emoji {
            font-size: 1.5rem;
            margin-right: 8px;
        }

        /* Learning Items */
        .learning {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin: 20px 0;
        }

        .learning-item {
            background: rgba(244, 63, 94, 0.1);
            border: 1px solid rgba(244, 63, 94, 0.3);
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            color: var(--text);
            transition: all 0.3s;
        }

        .learning-item:hover {
            background: rgba(244, 63, 94, 0.2);
            transform: translateY(-2px);
        }

        /* Contact Section */
        .contact {
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid rgba(14, 165, 233, 0.2);
            text-align: center;
        }

        .contact-link {
            display: inline-block;
            padding: 10px 20px;
            margin: 8px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: var(--bg);
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .contact-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.3);
        }

        /* Divider */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            margin: 40px 0;
        }

        @media (max-width: 600px) {
            h1 {
                font-size: 2rem;
            }
            
            .skills-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <h1>👋 Hi, I'm Khubaib Nazeer</h1>
        <p class="subtitle">Full-Stack Developer & Problem Solver</p>
        <p class="intro">
            Passionate about building efficient, scalable applications. I love tackling algorithmic challenges, writing clean code, and continuously learning new technologies. With expertise across the full stack, I'm dedicated to creating solutions that make a real impact.
        </p>

        <hr>

        <!-- About Me -->
        <h2>🚀 About Me</h2>
        <p style="color: var(--gray); line-height: 1.8; margin-top: 15px;">
            I'm a developer with strong foundation in both systems programming and web development. I excel at:<br><br>
            • Designing efficient algorithms and optimizing performance<br>
            • Building robust full-stack applications<br>
            • Implementing clean code and design patterns<br>
            • Data analysis and visualization<br>
        </p>

        <hr>

        <!-- Languages -->
        <h2>💻 Languages</h2>
        <div class="badges">
            <span class="badge">C++</span>
            <span class="badge">Python</span>
            <span class="badge">JavaScript</span>
            <span class="badge">Assembly</span>
            <span class="badge">HTML5</span>
            <span class="badge">CSS3</span>
        </div>

        <!-- Core Concepts -->
        <h2>🎯 Core Concepts</h2>
        <div class="badges">
            <span class="badge">Object-Oriented Programming</span>
            <span class="badge">Data Structures & Algorithms</span>
            <span class="badge">Design Patterns</span>
        </div>

        <!-- Databases & Tools -->
        <h2>🛠️ Tools & Technologies</h2>
        <div class="skills-container">
            <div class="skill-box">
                <div class="skill-title">🗄️ Databases</div>
                <div class="skill-items">
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">Query Optimization</span>
                </div>
            </div>

            <div class="skill-box">
                <div class="skill-title">📊 Data Science & Libraries</div>
                <div class="skill-items">
                    <span class="skill-tag">NumPy</span>
                    <span class="skill-tag">Pandas</span>
                    <span class="skill-tag">Matplotlib</span>
                </div>
            </div>

            <div class="skill-box">
                <div class="skill-title">📦 Version Control</div>
                <div class="skill-items">
                    <span class="skill-tag">Git</span>
                    <span class="skill-tag">GitHub</span>
                </div>
            </div>
        </div>

        <hr>

        <!-- What I Do -->
        <h2>⚡ What I Do</h2>
        <div class="features">
            <div class="feature-item">
                <span class="feature-emoji">🚀</span> <strong>Full-Stack Development</strong> — End-to-end applications
            </div>
            <div class="feature-item">
                <span class="feature-emoji">📈</span> <strong>Data Analysis</strong> — Processing & visualization
            </div>
            <div class="feature-item">
                <span class="feature-emoji">⚙️</span> <strong>Algorithm Design</strong> — Optimal solutions
            </div>
            <div class="feature-item">
                <span class="feature-emoji">🎨</span> <strong>Web Development</strong> — Responsive UIs
            </div>
            <div class="feature-item">
                <span class="feature-emoji">🏗️</span> <strong>Architecture</strong> — Clean & scalable
            </div>
            <div class="feature-item">
                <span class="feature-emoji">🔧</span> <strong>System Programming</strong> — Performance tuning
            </div>
        </div>

        <hr>

        <!-- Currently Exploring -->
        <h2>🌱 Currently Exploring</h2>
        <div class="learning">
            <div class="learning-item">🤖 Machine Learning & AI</div>
            <div class="learning-item">☁️ Cloud Computing</div>
            <div class="learning-item">🔐 Cybersecurity</div>
            <div class="learning-item">📱 Mobile Development</div>
            <div class="learning-item">🌐 Web3 Technology</div>
            <div class="learning-item">🧪 Open Source</div>
        </div>

        <hr>

        <!-- Contact -->
        <div class="contact">
            <h2 style="border: none; text-align: center; margin-bottom: 15px;">📫 Let's Connect!</h2>
            <p style="color: var(--gray); margin-top: 0;">Interested in collaboration or just want to chat? Feel free to reach out!</p>
            
            <div style="margin: 25px 0;">
                <a href="mailto:khubaibnazeer8@gmail.com" class="contact-link">📧 Email</a>
                <a href="https://www.linkedin.com/in/khubaib-nazeer/" class="contact-link">💼 LinkedIn</a>
                <a href="https://github.com" class="contact-link">🐙 GitHub</a>
            </div>

            <p style="margin-top: 40px; color: var(--gray); font-size: 0.9rem;">
                © 2024 Khubaib Nazeer | Designed & Built with ❤️
            </p>
        </div>
    </div>
</body>
</html>

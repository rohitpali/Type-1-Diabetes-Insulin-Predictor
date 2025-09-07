(function () {
  const toggleBtn = document.getElementById('chatbot-toggle');
  const panel = document.getElementById('chatbot-panel');
  const closeBtn = document.getElementById('chatbot-close');
  const body = document.getElementById('chatbot-body');

  const steps = [
    "Hi, Welcome! I will guide you step by step.",
    "Step 1: Please Sign Up or Login to continue.",
    "Step 2: Read the Instructions page carefully.",
    "Step 3: Go to Meals to estimate your calories if needed.",
    "tep 4: Open Predict page, fill important fields (Glucose, Carbs/hr, ICR, ISF, Weight, etc.) and hit Predict.",
    "Tip: Your result will appear on the right with safety checks."
  ];

  let currentStep = 0;

  function addMsg(text) {
    const div = document.createElement('div');
    div.className = 'chatbot-msg';
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function showStep(stepIndex) {
    body.innerHTML = '';
    addMsg(steps[stepIndex]);
    if (document.getElementById("chatbot-controls")) {
      document.getElementById("chatbot-controls").remove();
    }
    const controls = document.createElement("div");
    controls.id = "chatbot-controls";
    controls.style.marginTop = "10px";
    controls.style.textAlign = "right";

    if (stepIndex > 0) {
      const backBtn = document.createElement("button");
      backBtn.textContent = "⬅ Back";
      backBtn.className = "chatbot-btn";
      backBtn.onclick = () => {
        currentStep--;
        showStep(currentStep);
      };
      controls.appendChild(backBtn);
    }

    if (stepIndex < steps.length - 1) {
      const nextBtn = document.createElement("button");
      nextBtn.textContent = "Next ➡";
      nextBtn.className = "chatbot-btn";
      nextBtn.style.marginLeft = "5px";
      nextBtn.onclick = () => {
        currentStep++;
        showStep(currentStep);
      };
      controls.appendChild(nextBtn);
    }
    body.appendChild(controls);
  }

  if (toggleBtn && panel) {
    toggleBtn.addEventListener('click', () => {
      const showing = panel.style.display === 'block';
      panel.style.display = showing ? 'none' : 'block';
      if (!showing) {
        currentStep = 0;
        showStep(currentStep);
      }
    });
  }

  if (closeBtn) closeBtn.addEventListener('click', () => panel.style.display = 'none');

  // Auto open once on welcome page to onboard
  if (document.body.classList.contains('welcome-page')) {
    setTimeout(() => {
      if (panel && panel.style.display !== 'block') {
        panel.style.display = 'block';
        currentStep = 0;
        showStep(currentStep);
      }
    }, 600);
  }
})();

document.getElementById('submitBtn').addEventListener('click', function () {
    // 改用單一 Object，而非 Array
    const optimizedData = {};

    // 輔助函式：從題目文字中提取 [主題]
    // 例如："Q2. [前端開發] 針對..." -> "前端開發"
    function getTopic(fullText) {
        const match = fullText.match(/\[(.*?)\]/);
        return match ? match[1] : "其他";
    }

    // --- 處理 Q1 (核心語言) ---
    // 轉化為字串格式： "Python(2), JS(2)"
    const q1Parts = [];
    const q1Rows = document.querySelectorAll('#q1-container .skill-row');
    q1Rows.forEach(row => {
        const lang = row.querySelector('.lang-input').value.trim();
        const score = row.querySelector('.score-input').value;
        if (lang && score) {
            q1Parts.push(`${lang}(${score})`);
        }
    });
    // Key 格式：題號_主題
    optimizedData["Q1_核心語言"] = q1Parts.join(", ");


    // --- 處理 Q2-Q19, Q21-Q23 (單選/複選) ---
    const simpleQuestions = [
        "Q2", "Q3", "Q4", "Q5", "Q6", "Q7",
        "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15",
        "Q16", "Q17", "Q18", "Q19", "Q21", "Q22", "Q23"
    ];

    simpleQuestions.forEach(qid => {
        const container = document.querySelector(`div[data-qid="${qid}"]`);
        if (!container) return;

        const fullQuestionText = container.querySelector('.q-title').innerText;
        const topic = getTopic(fullQuestionText);
        const key = `${qid}_${topic}`; // 組合 Key: Q2_前端開發

        const inputs = container.querySelectorAll('input:checked');

        if (inputs.length === 0) {
            optimizedData[key] = "未作答";
        } else if (inputs.length === 1) {
            // 單選：直接存文字，例如 "B. 熟悉..."
            optimizedData[key] = inputs[0].closest('label').innerText.trim();
        } else {
            // 複選：合併為字串，例如 "A. xxx; B. ooo"
            const answers = Array.from(inputs).map(input => input.closest('label').innerText.trim());
            optimizedData[key] = answers.join("; ");
        }
    });

    // --- 處理 Q8 (Domain Knowledge) ---
    const q8Text = document.getElementById('q8-input').value.trim();
    optimizedData["Q8_領域專精"] = q8Text || "無";

    // --- 處理 Q20 (排序) ---
    // 轉化為： "1.Financial, 2.WLB, 3.Culture"
    const q20Values = [
        document.getElementById('q20-1'),
        document.getElementById('q20-2'),
        document.getElementById('q20-3')
    ].map((select, idx) => {
        if (select.value) return `${idx + 1}.${select.value}`; // 為了省 Token，這裡只存代號 (Financial)
        return null;
    }).filter(val => val); // 過濾空值

    optimizedData["Q20_價值觀排序"] = q20Values.join(", ");

    // --- 輸出結果 ---
    const jsonString = JSON.stringify(optimizedData, null, 2);
    document.getElementById('result-area').style.display = 'block';
    document.getElementById('json-output').value = jsonString;
});
import { Actor } from "apify";

await Actor.init();

const input = await Actor.getInput();
const { drugName, limit = 10 } = input || {};

if (!drugName) {
    console.error("drugName is required");
    await Actor.exit();
}

try {
    const url = `https://api.fda.gov/drug/enforcement.json?search=drug_name:"${encodeURIComponent(drugName)}"&limit=${limit}`;

    console.log(`Fetching FDA drug safety data for: ${drugName}`);
    const response = await fetch(url);
    const data = await response.json();

    if (data.results && Array.isArray(data.results)) {
        const results = data.results.map(item => ({
            drugName: item.drug_name || "N/A",
            manufacturer: item.manufacturer_name || "N/A",
            reason: item.reason_for_recall || "N/A",
            reportDate: item.report_date || "N/A",
            recallStatus: item.recall_status || "N/A",
            cdrssNumber: item.cdrss_number || "N/A",
            distributionPattern: item.distribution_pattern || "N/A"
        }));

        await Actor.pushData(results);
        try { await Actor.charge({ eventName: 'analysis-complete', count: 1 }); } catch (e) { console.error("Charge failed:", e.message); }
        console.log(`Pushed ${results.length} drug safety records`);
    } else {
        console.log("No results found");
        await Actor.pushData([]);
    }
} catch (error) {
    console.error("Error fetching FDA data:", error.message);
    await Actor.pushData([]);
}

await Actor.exit();
import { Actor } from "apify";

await Actor.init();

const input = await Actor.getInput();
const { name } = input || {};

if (!name) {
    console.error("name is required");
    await Actor.exit();
}

try {
    console.log(`Checking EU sanctions list for: ${name}`);

    // EU Sanctions consolidated list
    const url = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content";

    const response = await fetch(url);
    const xmlText = await response.text();

    // Simple string matching for XML
    const listed = xmlText.toLowerCase().includes(name.toLowerCase());

    const result = {
        name: name,
        euSanctioned: listed,
        checkedDate: new Date().toISOString(),
        source: "European External Action Service (EEAS) Sanctions Monitor"
    };

    await Actor.pushData([result]);
    try { await Actor.charge({ eventName: 'analysis-complete', count: 1 }); } catch (e) { console.error("Charge failed:", e.message); }
    console.log(`EU sanctions check completed for: ${name}`);
} catch (error) {
    console.error("Error checking EU sanctions:", error.message);
    await Actor.pushData([]);
}

await Actor.exit();
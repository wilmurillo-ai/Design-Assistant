import type { HearApiClient } from '@h-ear/core';
import {
    formatWebhookList, formatWebhookDetail, formatWebhookCreated,
    formatWebhookPing, formatWebhookDeliveries,
} from '../formatter.js';

export async function webhookListCommand(client: HearApiClient): Promise<string> {
    const result = await client.listEnterpriseWebhooks();
    return formatWebhookList(result);
}

export async function webhookDetailCommand(client: HearApiClient, webhookId: string): Promise<string> {
    const result = await client.getEnterpriseWebhook(webhookId);
    return formatWebhookDetail(result);
}

export async function webhookCreateCommand(
    client: HearApiClient,
    url: string,
    options?: {
        events?: string[];
        description?: string;
        taxonomyFilter?: string[];
        notificationTierDepth?: number;
        notificationTierValues?: string[];
    },
): Promise<string> {
    const result = await client.createEnterpriseWebhook({
        url,
        events: options?.events,
        description: options?.description,
        taxonomyFilter: options?.taxonomyFilter,
        notificationTierDepth: options?.notificationTierDepth,
        notificationTierValues: options?.notificationTierValues,
    });
    return formatWebhookCreated(result);
}

export async function webhookPingCommand(client: HearApiClient, webhookId: string): Promise<string> {
    const result = await client.pingEnterpriseWebhook(webhookId);
    return formatWebhookPing(result);
}

export async function webhookDeliveriesCommand(
    client: HearApiClient,
    webhookId: string,
    options?: { limit?: number },
): Promise<string> {
    const result = await client.getEnterpriseWebhookDeliveries(webhookId, options);
    return formatWebhookDeliveries(result);
}

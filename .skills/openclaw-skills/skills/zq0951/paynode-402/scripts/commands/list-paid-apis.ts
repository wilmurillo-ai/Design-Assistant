import { MarketplaceClient } from '../marketplace/client.ts';
import { jsonEnvelope, reportError, EXIT_CODES, BaseCliOptions } from '../utils.ts';

interface ListPaidApisOptions extends BaseCliOptions {
  limit?: string | number;
  tag?: string | string[];
  seller?: string;
}

export async function listPaidApisAction(options: ListPaidApisOptions) {
  const isJson = !!options.json;

  try {
    const client = new MarketplaceClient({
      baseUrl: options.marketUrl,
      json: isJson
    });

    const tags = Array.isArray(options.tag)
      ? options.tag
      : options.tag
        ? [options.tag]
        : [];

    const result = await client.listCatalog({
      network: options.network,
      limit: options.limit ? Number(options.limit) : undefined,
      tag: tags,
      seller: options.seller
    });

    if (isJson) {
      console.log(jsonEnvelope({
        status: 'success',
        total: result.total || result.items.length,
        items: result.items
      }));
      return;
    }

    if (result.items.length === 0) {
      console.log('No paid APIs found.');
      return;
    }

    for (const item of result.items) {
      const price = item.price_per_call ? `${item.price_per_call} ${item.currency || 'USDC'}` : 'unpriced';
      const network = item.network || 'unspecified';
      const tagsLine = item.tags && item.tags.length > 0 ? ` [${item.tags.join(', ')}]` : '';
      console.log(`- ${item.id}: ${item.name} | ${price} | ${network}${tagsLine}`);
      if (item.description) {
        console.log(`  ${item.description}`);
      }
    }
  } catch (error: any) {
    reportError(error, isJson, EXIT_CODES.NETWORK_ERROR);
  }
}

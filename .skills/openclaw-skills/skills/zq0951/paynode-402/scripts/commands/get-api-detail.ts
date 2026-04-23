import { MarketplaceClient } from '../marketplace/client.ts';
import { jsonEnvelope, reportError, EXIT_CODES, BaseCliOptions } from '../utils.ts';

interface GetApiDetailOptions extends BaseCliOptions {
}

export async function getApiDetailAction(apiId: string, options: GetApiDetailOptions) {
  const isJson = !!options.json;

  try {
    const client = new MarketplaceClient({
      baseUrl: options.marketUrl,
      json: isJson
    });

    const detail = await client.getApiDetail(apiId, options.network);

    if (isJson) {
      console.log(jsonEnvelope({
        status: 'success',
        api: detail
      }));
      return;
    }

    console.log(JSON.stringify(detail, null, 2));
  } catch (error: any) {
    reportError(error, isJson, EXIT_CODES.NETWORK_ERROR);
  }
}

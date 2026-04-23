/**
 * mofang_list_spaces — 列出所有空间
 */
export interface SpaceItem {
    label: string;
    id: string;
}
export interface ListSpacesResult {
    success: boolean;
    message: string;
    data?: SpaceItem[];
}
export declare function handler(_params: object, context: {
    config: Record<string, string>;
}): Promise<ListSpacesResult>;
//# sourceMappingURL=spaces.d.ts.map
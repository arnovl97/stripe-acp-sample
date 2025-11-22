/**
 * HTML Views for ACP Seller Backend
 * Contains HTML templates for serving documentation pages
 */

/**
 * Returns the HTML for the root endpoint documentation page
 * @returns HTML string with endpoint documentation
 */
export function getIndexPageHtml(): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACP Seller Backend</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 8px; max-width: 900px; }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            .endpoint { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; }
            .endpoint p { margin: 8px 0; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .post { background: #49cc90; color: white; }
            .get { background: #61affe; color: white; }
            code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
            strong { color: #333; }
            .type-def { background: #f0f0f0; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 0.9em; }
            .type-def code { background: transparent; padding: 0; }
            .optional { color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ACP Seller Backend</h1>
            <p>Agentic Commerce Protocol seller backend implementation for managing checkout sessions.</p>
            
            <h2>Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/products</code>
                <p><strong>List products</strong></p>
                <p><strong>Returns:</strong></p>
                <div class="type-def">
                    <code>{<br>
                    &nbsp;&nbsp;products: Product[]<br>
                    }</code>
                </div>
                <p><strong>Product:</strong></p>
                <div class="type-def">
                    <code>{<br>
                    &nbsp;&nbsp;id: string,<br>
                    &nbsp;&nbsp;name: string,<br>
                    &nbsp;&nbsp;price: number (cents),<br>
                    &nbsp;&nbsp;description: string,<br>
                    &nbsp;&nbsp;stock: number,<br>
                    &nbsp;&nbsp;image: string (uri)<br>
                    }</code>
                </div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/checkout_sessions</code>
                <p><strong>Create a new checkout session</strong></p>
                <p><strong>Body:</strong></p>
                <div class="type-def">
                    <code>{<br>
                    &nbsp;&nbsp;items: Item[],<br>
                    &nbsp;&nbsp;<span class="optional">buyer?: Buyer,</span><br>
                    &nbsp;&nbsp;<span class="optional">fulfillment_address?: Address</span><br>
                    }</code>
                </div>
                <p><strong>Item:</strong> <code>{ id: string, quantity: number }</code></p>
                <p><strong>Buyer:</strong> <code>{ first_name: string, last_name: string, email: string, phone_number?: string }</code></p>
                <p><strong>Address:</strong> <code>{ name: string, line_one: string, line_two?: string, city: string, state: string, country: string, postal_code: string }</code></p>
                <p><strong>Returns:</strong> <code>CheckoutSession</code> (201)</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/checkout_sessions/:checkout_session_id</code>
                <p><strong>Retrieve a checkout session</strong></p>
                <p><strong>Path:</strong> <code>checkout_session_id: string</code></p>
                <p><strong>Returns:</strong> <code>CheckoutSession</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/checkout_sessions/:checkout_session_id</code>
                <p><strong>Update a checkout session</strong></p>
                <p><strong>Path:</strong> <code>checkout_session_id: string</code></p>
                <p><strong>Body:</strong></p>
                <div class="type-def">
                    <code>{<br>
                    &nbsp;&nbsp;<span class="optional">items?: Item[],</span><br>
                    &nbsp;&nbsp;<span class="optional">buyer?: Buyer,</span><br>
                    &nbsp;&nbsp;<span class="optional">fulfillment_address?: Address,</span><br>
                    &nbsp;&nbsp;<span class="optional">fulfillment_option_id?: string</span><br>
                    }</code>
                </div>
                <p><strong>Returns:</strong> <code>CheckoutSession</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/checkout_sessions/:checkout_session_id/complete</code>
                <p><strong>Complete a checkout session</strong></p>
                <p><strong>Path:</strong> <code>checkout_session_id: string</code></p>
                <p><strong>Body:</strong></p>
                <div class="type-def">
                    <code>{<br>
                    &nbsp;&nbsp;payment_data: { token: string },<br>
                    &nbsp;&nbsp;<span class="optional">buyer?: Buyer</span><br>
                    }</code>
                </div>
                <p><strong>Returns:</strong> <code>CheckoutSessionWithOrder</code> (CheckoutSession + <code>{ order: { id: string, checkout_session_id: string, permalink_url: string } }</code>)</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/checkout_sessions/:checkout_session_id/cancel</code>
                <p><strong>Cancel a checkout session</strong></p>
                <p><strong>Path:</strong> <code>checkout_session_id: string</code></p>
                <p><strong>Returns:</strong> <code>CheckoutSession</code></p>
            </div>
        </div>
    </body>
    </html>
  `;
}


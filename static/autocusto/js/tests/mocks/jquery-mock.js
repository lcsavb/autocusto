/**
 * jQuery Mock for med.js Testing
 * 
 * Provides a minimal jQuery implementation to test med.js logic
 * without requiring a real DOM or jQuery library.
 */

// jQuery element mock
class JQueryElement {
    constructor(selector) {
        this.selector = selector;
        this._value = '';
        this._attributes = {};
        this._classes = [];
        
        // Chainable methods
        this.val = jest.fn().mockImplementation((value) => {
            if (value !== undefined) {
                this._value = value;
                return this;
            }
            return this._value;
        });
        
        this.attr = jest.fn().mockImplementation((name, value) => {
            if (value !== undefined) {
                this._attributes[name] = value;
                return this;
            }
            return this._attributes[name];
        });
        
        this.removeAttr = jest.fn().mockImplementation((name) => {
            delete this._attributes[name];
            return this;
        });
        
        this.addClass = jest.fn().mockImplementation((className) => {
            if (!this._classes.includes(className)) {
                this._classes.push(className);
            }
            return this;
        });
        
        this.removeClass = jest.fn().mockImplementation((className) => {
            this._classes = this._classes.filter(c => c !== className);
            return this;
        });
        
        this.hasClass = jest.fn().mockImplementation((className) => {
            return this._classes.includes(className);
        });
        
        this.fill = jest.fn().mockImplementation((value) => {
            this._value = value;
            return this;
        });
        
        this.prop = jest.fn().mockReturnThis();
        this.each = jest.fn().mockReturnThis();
        this.on = jest.fn().mockReturnThis();
        this.click = jest.fn().mockReturnThis();
        this.change = jest.fn().mockReturnThis();
        this.keyup = jest.fn().mockReturnThis();
        this.toggle = jest.fn().mockReturnThis();
        this.toggleClass = jest.fn().mockReturnThis();
        this.find = jest.fn().mockReturnThis();
        this.parent = jest.fn().mockReturnThis();
        this.append = jest.fn().mockReturnThis();
        this.length = 1;
        this.count = jest.fn().mockReturnValue(1);
    }
}

// Main jQuery mock function
const jQueryMock = jest.fn().mockImplementation((selector) => {
    if (typeof selector === 'function') {
        // Document ready handler
        setTimeout(selector, 0);
        return;
    }
    
    if (typeof selector === 'object' && selector !== null) {
        // $(this) or $(element) - return mock element
        return new JQueryElement('element');
    }
    
    // $(selector) - return mock element
    return new JQueryElement(selector);
});

// jQuery static methods
jQueryMock.fn = {
    on: jest.fn(),
    each: jest.fn(),
    removeAttr: jest.fn(),
    attr: jest.fn(),
    val: jest.fn(),
    prop: jest.fn(),
    addClass: jest.fn(),
    removeClass: jest.fn(),
    hasClass: jest.fn(),
    click: jest.fn(),
    change: jest.fn(),
    keyup: jest.fn()
};

// Document ready simulation
jQueryMock.ready = jest.fn().mockImplementation((callback) => {
    setTimeout(callback, 0);
});

// Event handling
jQueryMock.Event = jest.fn();

module.exports = jQueryMock;
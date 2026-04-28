
/*
 * Copyright (c) 2020, GlobalLogic Ukraine LLC
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 1. Redistributions of source code must retain the above copyright
 *	  notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *	  notice, this list of conditions and the following disclaimer in the
 *	  documentation and/or other materials provided with the distribution.
 * 3. All advertising materials mentioning features or use of this software
 *	  must display the following acknowledgment:
 *	  This product includes software developed by the GlobalLogic.
 * 4. Neither the name of the GlobalLogic nor the
 *	  names of its contributors may be used to endorse or promote products
 *	  derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY GLOBALLOGIC UKRAINE LLC ``AS IS`` AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL GLOBALLOGIC UKRAINE LLC BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <linux/init.h>
#include <linux/types.h>
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/ktime.h>
#include <linux/slab.h>
#include <linux/proc_fs.h>

#include <hello1.h>

MODULE_AUTHOR("Kyryl Larchenko <fkirill440@gmail.com>");
MODULE_DESCRIPTION("Memory management in Linux Kernel Training");
MODULE_LICENSE("Dual BSD/GPL");

static LIST_HEAD(head);
static int print_count = 0;

int procfile_read(struct file *filp, char *buf, size_t count, loff_t *offp)
{
    int len = 0;

    len = sprintf(buf, "\nNumber of salutes: %d\n", print_count);
    return len;
}

int print_hello(uint times)
{
	int i;
	struct hello_list *tail, *tmp;

	if (times <= 0) {
		pr_warn("Input is zero or negative. No output.\n");
		return 0;
	}

	if (times >= 5 && times <= 10)
		pr_warn("Input is between 5 and 10.\n");

	if (times > 10) {
		pr_err("Input is greater than ten. Aborting...\n");
        BUG();
		return -EINVAL;
	}
    print_count = times;

	for (i = 0; i < times; ++i) {
		tail = kmalloc(sizeof(struct hello_list), GFP_KERNEL);
        if (ZERO_OR_NULL_PTR(tail))
            goto error;
		tail->t_enter = ktime_get();
		pr_info("Salutations, Linux memory allocation!\n");
		tail->t_exit = ktime_get();
        list_add_tail(&(tail->node), &head);
	}

	return 0;

error: 
    pr_err("kmalloc(): out of memory\n");
    list_for_each_entry_safe(tail, tmp, &head, node) {
        list_del(&(tail->node));
        kfree(tail);
    }
}
EXPORT_SYMBOL(print_hello);

static const struct file_operations fops = {
owner: THIS_MODULE,
read:  procfile_read
};

static int __init hello1_init(void)
{
    proc_create("hello1info", 0, NULL, &fops);
	return 0;
}

static void __exit hello1_exit(void)
{
	struct hello_list *tail, *tmp;

    list_for_each_entry_safe(tail, tmp, &head, node) {
        pr_info("Salute length: %lld\n", tail->t_exit - tail->t_enter);

        list_del(&(tail->node));
        kfree(tail);
    }

    remove_proc_entry("hello1info", NULL);
}

module_init(hello1_init);
module_exit(hello1_exit);


